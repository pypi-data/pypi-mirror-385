"""Abstract benchmark module class that the model classes inherit from."""

import collections.abc as c
import logging
import re
import typing as t
from abc import ABC, abstractmethod
from functools import cached_property, partial

from datasets import Dataset, DatasetDict
from torch import nn

from ..enums import TaskGroup
from ..exceptions import InvalidBenchmark, NeedsEnvironmentVariable, NeedsExtraInstalled
from ..logging_utils import get_pbar, log_once
from ..task_group_utils import (
    question_answering,
    sequence_classification,
    text_to_text,
    token_classification,
)

if t.TYPE_CHECKING:
    from transformers.tokenization_utils import PreTrainedTokenizer
    from transformers.trainer import Trainer

    from ..data_models import (
        BenchmarkConfig,
        DatasetConfig,
        GenerativeModelOutput,
        ModelConfig,
        Task,
    )
    from ..enums import BatchingPreference, GenerativeType
    from ..types import ComputeMetricsFunction, ExtractLabelsFunction


class BenchmarkModule(ABC):
    """Abstract class for a benchmark module.

    Attributes:
        model_config:
            The model configuration.
        dataset_config:
            The dataset configuration.
        benchmark_config:
            The benchmark configuration.
        buffer:
            A buffer to store temporary data.
    """

    fresh_model: bool
    batching_preference: "BatchingPreference"
    high_priority: bool
    allowed_params: dict[re.Pattern, list[str]] = {re.compile(r".*"): []}

    def __init__(
        self,
        model_config: "ModelConfig",
        dataset_config: "DatasetConfig",
        benchmark_config: "BenchmarkConfig",
        log_metadata: bool = True,
    ) -> None:
        """Initialise the benchmark module.

        Args:
            model_config:
                The model configuration.
            dataset_config:
                The dataset configuration.
            benchmark_config:
                The benchmark configuration.
            log_metadata:
                Whether to log the metadata of the model.
        """
        self.model_config = model_config
        self.dataset_config = dataset_config
        self.benchmark_config = benchmark_config
        self.log_metadata = log_metadata
        self.buffer: dict[str, t.Any] = dict()
        if self.log_metadata:
            self._log_metadata()

    def _log_metadata(self) -> None:
        """Log the metadata of the model."""
        logging_msg: str = "    ↳ "
        if self.num_params < 0:
            logging_msg += "The model has an unknown number of parameters, "
        else:
            logging_msg += f"The model has {self.num_params:,} parameters, "
        if self.vocab_size < 0:
            logging_msg += "an unknown vocabulary size, "
        else:
            logging_msg += f"a vocabulary size of {self.vocab_size:,}, "
        if self.model_max_length < 0:
            logging_msg += "and an unknown maximum sequence length."
        else:
            logging_msg += f"and a maximum context length of {self.model_max_length:,}."
        log_once(message=logging_msg, level=logging.INFO)

    def get_pytorch_module(self) -> "nn.Module":
        """Get the underlying PyTorch module.

        Returns:
            The PyTorch module.
        """
        if hasattr(self, "_model"):
            return self._model
        raise NotImplementedError(
            "The `get_pytorch_module` method has not been implemented for "
            f"{self.__class__.__name__}."
        )

    def get_tokeniser(self) -> "PreTrainedTokenizer":
        """Get the underlying tokeniser.

        Returns:
            The tokeniser.
        """
        if hasattr(self, "_tokeniser"):
            return self._tokeniser
        raise NotImplementedError(
            "The `get_tokeniser` method has not been implemented for "
            f"{self.__class__.__name__}."
        )

    @cached_property
    @abstractmethod
    def num_params(self) -> int:
        """The number of parameters in the model.

        Returns:
            The number of parameters in the model.
        """
        ...

    @property
    @abstractmethod
    def generative_type(self) -> "GenerativeType | None":
        """Get the generative type of the model.

        Returns:
            The generative type of the model, or None if the model is not generative.
        """
        ...

    @cached_property
    @abstractmethod
    def vocab_size(self) -> int:
        """The vocabulary size of the model.

        Returns:
            The vocabulary size of the model.
        """
        ...

    @cached_property
    @abstractmethod
    def model_max_length(self) -> int:
        """The maximum length of the model.

        Returns:
            The maximum length of the model.
        """
        ...

    @property
    @abstractmethod
    def data_collator(self) -> c.Callable[[list[t.Any]], dict[str, t.Any]]:
        """The data collator used to prepare samples during finetuning.

        Returns:
            The data collator.
        """
        ...

    @property
    def compute_metrics(self) -> "ComputeMetricsFunction":
        """The function used to compute the metrics.

        Returns:
            The function used to compute the metrics.
        """
        match self.dataset_config.task.task_group:
            case TaskGroup.SEQUENCE_CLASSIFICATION:
                return partial(
                    sequence_classification.compute_metrics,
                    dataset_config=self.dataset_config,
                    benchmark_config=self.benchmark_config,
                )
            case TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION:
                return partial(
                    sequence_classification.compute_metrics,
                    dataset_config=self.dataset_config,
                    benchmark_config=self.benchmark_config,
                )
            case TaskGroup.TEXT_TO_TEXT:
                return partial(
                    text_to_text.compute_metrics,
                    dataset_config=self.dataset_config,
                    benchmark_config=self.benchmark_config,
                )
            case TaskGroup.TOKEN_CLASSIFICATION:
                return partial(
                    token_classification.compute_metrics,
                    has_misc_tags=self.buffer.get("has_misc_tags", True),
                    dataset_config=self.dataset_config,
                    benchmark_config=self.benchmark_config,
                )
            case TaskGroup.QUESTION_ANSWERING:
                return partial(
                    question_answering.compute_metrics,
                    dataset_config=self.dataset_config,
                    benchmark_config=self.benchmark_config,
                )
            case _:
                raise NotImplementedError(
                    f"Unsupported task group: {self.dataset_config.task.task_group}."
                )

    @property
    @abstractmethod
    def extract_labels_from_generation(self) -> "ExtractLabelsFunction":
        """The function used to extract the labels from the generated output.

        Returns:
            The function used to extract the labels from the generated output.
        """
        ...

    @property
    @abstractmethod
    def trainer_class(self) -> t.Type["Trainer"]:
        """The Trainer class to use for finetuning.

        Returns:
            The Trainer class.
        """
        ...

    def prepare_datasets(
        self, datasets: list[DatasetDict], task: "Task"
    ) -> list[DatasetDict]:
        """Prepare the datasets for the model.

        This includes things like tokenisation.

        Args:
            datasets:
                The datasets to prepare.
            task:
                The task to prepare the datasets for.

        Returns:
            The prepared datasets.

        Raises:
            InvalidBenchmark:
                If the dataset does not have a 'train' split for token classification
                tasks.
        """
        for idx, dataset in enumerate(
            get_pbar(iterable=datasets, desc="Preparing datasets")
        ):
            prepared_dataset = self.prepare_dataset(
                dataset=dataset, task=task, itr_idx=idx
            )
            if self.dataset_config.task.task_group == TaskGroup.TOKEN_CLASSIFICATION:
                if "train" not in dataset:
                    raise InvalidBenchmark(
                        "The dataset does not have a 'train' split, which is required "
                        "for token classification tasks."
                    )
                labels_in_train: set[str] = {
                    tag for tag_list in dataset["train"]["labels"] for tag in tag_list
                }
                self.buffer["has_misc_tags"] = (
                    "B-MISC" in labels_in_train or "I-MISC" in labels_in_train
                )

            datasets_dict: dict[str, Dataset] = dict()
            for split_name, split in prepared_dataset.items():
                datasets_dict[split_name] = split
            for split_name, split in dataset.items():
                datasets_dict[f"original_{split_name}"] = split
            datasets[idx] = DatasetDict(datasets_dict)
        return datasets

    @abstractmethod
    def prepare_dataset(
        self, dataset: DatasetDict, task: "Task", itr_idx: int
    ) -> DatasetDict:
        """Prepare the dataset for the model.

        This includes things like tokenisation.

        Args:
            dataset:
                The dataset to prepare.
            task:
                The task to prepare the dataset for.
            itr_idx:
                The index of the dataset in the iterator.

        Returns:
            The prepared dataset.
        """
        ...

    def generate(self, inputs: dict) -> "GenerativeModelOutput":
        """Generate outputs from the model.

        Args:
            inputs:
                A batch of inputs to pass through the model.

        Returns:
            The generated model outputs.
        """
        raise NotImplementedError(
            "The `generate` method has not been implemented for "
            f"{self.__class__.__name__}."
        )

    @classmethod
    @abstractmethod
    def model_exists(
        cls, model_id: str, benchmark_config: "BenchmarkConfig"
    ) -> bool | NeedsExtraInstalled | NeedsEnvironmentVariable:
        """Check if a model exists.

        Args:
            model_id:
                The model ID.
            benchmark_config:
                The benchmark configuration.

        Returns:
            Whether the model exists, or an error describing why we cannot check
            whether the model exists.
        """
        ...

    @classmethod
    @abstractmethod
    def get_model_config(
        cls, model_id: str, benchmark_config: "BenchmarkConfig"
    ) -> "ModelConfig":
        """Fetch the model configuration.

        Args:
            model_id:
                The model ID.
            benchmark_config:
                The benchmark configuration.

        Returns:
            The model configuration.
        """
        ...
