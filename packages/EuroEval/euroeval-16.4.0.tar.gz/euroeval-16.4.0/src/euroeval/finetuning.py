"""Functions related to the finetuning of models."""

import logging
import sys
import typing as t
from functools import partial

import torch
from transformers.trainer_callback import (
    EarlyStoppingCallback,
    PrinterCallback,
    ProgressCallback,
)
from transformers.trainer_utils import IntervalStrategy
from transformers.training_args import OptimizerNames, TrainingArguments

from .callbacks import NeverLeaveProgressCallback
from .enums import DataType
from .exceptions import InvalidBenchmark, NaNValueInModelOutput
from .logging_utils import block_terminal_output, get_pbar, log, log_once
from .model_loading import load_model
from .utils import clear_memory, enforce_reproducibility

if t.TYPE_CHECKING:
    from datasets import DatasetDict

    from .benchmark_modules import BenchmarkModule
    from .data_models import BenchmarkConfig, DatasetConfig, ModelConfig


def finetune(
    model: "BenchmarkModule",
    datasets: list["DatasetDict"],
    model_config: "ModelConfig",
    dataset_config: "DatasetConfig",
    benchmark_config: "BenchmarkConfig",
) -> list[dict[str, float]]:
    """Evaluate a model on a dataset through finetuning.

    Args:
        model:
            The model to evaluate.
        datasets:
            The datasets to use for training and evaluation.
        model_config:
            The configuration of the model.
        dataset_config:
            The dataset configuration.
        benchmark_config:
            The benchmark configuration.

    Returns:
        A list of dicts containing the scores for each metric for each iteration.

    Raises:
        InvalidBenchmark:
            If the benchmark could not be completed.
    """
    # Set the data type to use for the model weights
    using_cuda = benchmark_config.device == torch.device("cuda")
    if using_cuda and torch.cuda.is_bf16_supported():
        dtype = DataType.BF16
    elif using_cuda:
        dtype = DataType.FP16
    else:
        dtype = DataType.FP32

    bs: int = benchmark_config.batch_size
    scores: list[dict[str, float]] = list()
    for idx in get_pbar(
        iterable=range(benchmark_config.num_iterations),
        desc="Benchmarking",
        disable=not benchmark_config.progress_bar,
    ):
        # Set variable that tracks whether we need to initialize new models in
        # the single iteration call
        model_already_initialized = idx == 0

        # Run a loop here to deal with automatic reduction of batch size
        for _ in range(num_attempts := 10):
            # Clear GPU memory
            if not model_already_initialized:
                try:
                    del model
                except UnboundLocalError:
                    pass
                clear_memory()

            try:
                # Re-block terminal output, as it gets unblocked by the `transformers`
                # package before training
                block_terminal_output()

                training_args = get_training_args(
                    benchmark_config=benchmark_config,
                    model_config=model_config,
                    iteration_idx=idx,
                    dtype=dtype,
                    batch_size=bs,
                )

                itr_scores = finetune_single_iteration(
                    model=model if model_already_initialized else None,
                    dataset=datasets[idx],
                    training_args=training_args,
                    model_config=model_config,
                    dataset_config=dataset_config,
                    benchmark_config=benchmark_config,
                )

                scores.append(itr_scores)
                log(
                    f"Test scores for iteration {idx}: {itr_scores}",
                    level=logging.DEBUG,
                )

                break

            # NaN values can appear in the model output when using mixed precision, as
            # the hidden states get overflowed. In this case we try to disable mixed
            # precision and try again.
            except NaNValueInModelOutput as e:
                if dtype != DataType.FP32:
                    dtype = DataType.FP32
                    model_already_initialized = False
                    log(
                        "NaN value detected in model outputs while using mixed "
                        "precision. Retrying with full fp32 precision.",
                        level=logging.DEBUG,
                    )
                else:
                    raise InvalidBenchmark(
                        "NaN value detected in model outputs, even with mixed "
                        "precision disabled."
                    ) from e

            except Exception as e:
                if "CUDA" not in str(e) and "out of memory" not in str(e):
                    raise InvalidBenchmark(str(e)) from e

                if bs <= 1:
                    msg = "Could not benchmark the model, even with a batch size of 1!"
                    if "MPS" in str(e):
                        msg += (
                            " As you are using MPS, you can try running the evaluation "
                            "with the `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` "
                            "environment variable set, as this removes the upper bound "
                            "on the memory usage."
                        )
                    raise InvalidBenchmark(msg) from e

                model_already_initialized = False

                bs //= 2
                log(f"Reduced batch size to {bs}", level=logging.DEBUG)

        else:
            raise InvalidBenchmark(
                f"Could not benchmark the model after {num_attempts} attempts!"
            )

    return scores


def finetune_single_iteration(
    model: "BenchmarkModule | None",
    dataset: "DatasetDict",
    training_args: "TrainingArguments",
    model_config: "ModelConfig",
    dataset_config: "DatasetConfig",
    benchmark_config: "BenchmarkConfig",
) -> dict[str, float]:
    """Run a single iteration of a benchmark.

    Args:
        model:
            The model to use in the benchmark. If None then a new model will be loaded.
        dataset:
            The dataset to use for training and evaluation.
        training_args:
            The training arguments.
        model_config:
            The model configuration.
        dataset_config:
            The dataset configuration.
        benchmark_config:
            The benchmark configuration.

    Returns:
        The scores for the test dataset.
    """
    # Set random seeds to enforce reproducibility of the randomly initialised weights
    enforce_reproducibility(seed=training_args.seed)

    if model is None:
        model = load_model(
            model_config=model_config,
            dataset_config=dataset_config,
            benchmark_config=benchmark_config,
        )

    trainer = model.trainer_class(
        model=model.get_pytorch_module(),
        processing_class=model.get_tokeniser(),
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["val"],
        compute_metrics=partial(model.compute_metrics, dataset=None),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
        data_collator=model.data_collator,
        preprocess_logits_for_metrics=remove_extra_tensors_from_logits,
    )

    if not benchmark_config.verbose:

        def no_logging(logs: dict[str, float], start_time: float | None = None) -> None:
            return

        trainer.log = no_logging

    # Re-block terminal output, as it gets unblocked by the `transformers` package
    # before training
    block_terminal_output()

    # Sort out callbacks. We remove the callbacks that are producing unnecessary output,
    # to avoid cluttering the terminal output
    if not benchmark_config.verbose:
        trainer.remove_callback(PrinterCallback)
    trainer.remove_callback(ProgressCallback)
    if benchmark_config.progress_bar:
        trainer.add_callback(NeverLeaveProgressCallback)

    # Train the model
    trainer.train()

    # Evaluate the model
    with torch.inference_mode():
        try:
            test_scores = trainer.evaluate(
                eval_dataset=dataset["test"],
                orig_eval_dataset=dataset["original_test"],
                metric_key_prefix="test",
            )
        except TypeError:
            test_scores = trainer.evaluate(
                eval_dataset=dataset["test"], metric_key_prefix="test"
            )
        except NaNValueInModelOutput as e:
            del trainer
            del model
            clear_memory()
            raise e
        except (RuntimeError, ValueError, IndexError) as e:
            raise InvalidBenchmark(str(e)) from e

    return test_scores


def get_training_args(
    benchmark_config: "BenchmarkConfig",
    model_config: "ModelConfig",
    iteration_idx: int,
    dtype: DataType,
    batch_size: int | None = None,
) -> "TrainingArguments":
    """Get the training arguments for the current iteration.

    Args:
        benchmark_config:
            The benchmark configuration.
        model_config:
            The model configuration.
        iteration_idx:
            The index of the current iteration. This is only used to generate a
            unique random seed for the current iteration.
        dtype:
            The data type to use for the model weights.
        batch_size:
            The batch size to use for the current iteration, or None if the batch size
            in the benchmark config should be used.

    Returns:
        The training arguments for the current iteration.
    """
    log_once(message=f"Using {dtype} data type.", level=logging.DEBUG)

    if benchmark_config.verbose:
        logging_strategy = IntervalStrategy.STEPS
    else:
        logging_strategy = IntervalStrategy.NO

    if batch_size is None:
        batch_size = benchmark_config.batch_size

    training_args = TrainingArguments(
        output_dir=model_config.model_cache_dir,
        eval_strategy=IntervalStrategy.STEPS,
        logging_strategy=logging_strategy,
        save_strategy=IntervalStrategy.STEPS,
        eval_steps=30,
        logging_steps=30,
        save_steps=30,
        max_steps=1 if hasattr(sys, "_called_from_test") else 10_000,
        use_cpu=benchmark_config.device == torch.device("cpu"),
        report_to=[],
        save_total_limit=1,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        eval_accumulation_steps=32,
        optim=OptimizerNames.ADAMW_TORCH,
        learning_rate=2e-5,
        warmup_ratio=0.01,
        gradient_accumulation_steps=32 // batch_size,
        load_best_model_at_end=True,
        seed=4242 + iteration_idx,
        fp16=dtype == DataType.FP16,
        bf16=dtype == DataType.BF16,
        disable_tqdm=not benchmark_config.progress_bar,
        ddp_find_unused_parameters=False,
        save_safetensors=False,
    )

    # TEMP: Use only 1 GPU for now for finetuning
    if benchmark_config.device == torch.device("cuda"):
        training_args._n_gpu = 1

    return training_args


def remove_extra_tensors_from_logits(
    logits: torch.Tensor | tuple[torch.Tensor, ...], labels: torch.Tensor
) -> torch.Tensor | tuple[torch.Tensor, ...]:
    """If the logits are a tuple, return only the first element.

    Args:
        logits:
            The logits to process.
        labels:
            The labels to use for the processing.

    Returns:
        The processed logits.
    """
    if isinstance(logits, tuple) and isinstance(logits[-1], tuple):
        logits = logits[:-1]
        if len(logits) == 1:
            logits = logits[0]
    return logits
