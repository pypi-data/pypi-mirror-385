"""Freshly initialised encoder models."""

import re
import typing as t
from functools import cached_property
from json import JSONDecodeError

from transformers.models.auto.configuration_auto import AutoConfig
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.models.electra import (
    ElectraForQuestionAnswering,
    ElectraForSequenceClassification,
    ElectraForTokenClassification,
)
from transformers.models.xlm_roberta import (
    XLMRobertaForQuestionAnswering,
    XLMRobertaForSequenceClassification,
    XLMRobertaForTokenClassification,
)

from ..data_models import ModelConfig
from ..enums import InferenceBackend, ModelType, TaskGroup
from ..exceptions import (
    InvalidBenchmark,
    InvalidModel,
    NeedsEnvironmentVariable,
    NeedsExtraInstalled,
)
from ..generation_utils import raise_if_wrong_params
from ..logging_utils import block_terminal_output
from ..utils import create_model_cache_dir, get_hf_token
from .hf import (
    HuggingFaceEncoderModel,
    align_model_and_tokeniser,
    setup_model_for_question_answering,
)

if t.TYPE_CHECKING:
    from transformers.configuration_utils import PretrainedConfig
    from transformers.modeling_utils import PreTrainedModel
    from transformers.tokenization_utils import PreTrainedTokenizer

    from ..data_models import BenchmarkConfig, DatasetConfig


class FreshEncoderModel(HuggingFaceEncoderModel):
    """A freshly initialised encoder model."""

    fresh_model = True
    allowed_params = {re.compile(r".*"): ["slow-tokenizer"]}

    def __init__(
        self,
        model_config: "ModelConfig",
        dataset_config: "DatasetConfig",
        benchmark_config: "BenchmarkConfig",
        log_metadata: bool = True,
    ) -> None:
        """Initialise the model.

        Args:
            model_config:
                The model configuration.
            dataset_config:
                The dataset configuration.
            benchmark_config:
                The benchmark configuration.
            log_metadata:
                Whether to log metadata about the model and the benchmark.
        """
        raise_if_wrong_params(
            model_config=model_config, allowed_params=self.allowed_params
        )

        # This is already set when calling `super.__init__`, but we need it to get a
        # value from `self.model_max_length`, so we set it here as well.
        self.model_config = model_config

        model, tokeniser = load_model_and_tokeniser(
            model_config=model_config,
            dataset_config=dataset_config,
            benchmark_config=benchmark_config,
            model_max_length=self.model_max_length,
        )
        self._model: "PreTrainedModel" = model
        self._tokeniser: "PreTrainedTokenizer" = tokeniser

        self._model, self._tokeniser = align_model_and_tokeniser(
            model=self._model,
            tokeniser=self._tokeniser,
            model_max_length=self.model_max_length,
            raise_errors=benchmark_config.raise_errors,
        )

        # We specify `HuggingFaceEncoderModel` here instead of `VLLMModel`, as we want
        # to call the `__init__` method of the `BenchmarkModule` class.
        super(HuggingFaceEncoderModel, self).__init__(
            model_config=model_config,
            dataset_config=dataset_config,
            benchmark_config=benchmark_config,
            log_metadata=log_metadata,
        )

    @cached_property
    def num_params(self) -> int:
        """The number of parameters in the model.

        Returns:
            The number of parameters in the model.
        """
        match self.model_config.model_id:
            case "fresh-xlm-roberta-base":
                return 278_885_778
            case "fresh-electra-small":
                return 13_738_755
            case _:
                raise NotImplementedError(
                    f"Number of parameters for model {self.model_config.model_id} is "
                    "not implemented."
                )

    @cached_property
    def vocab_size(self) -> int:
        """The vocabulary size of the model.

        Returns:
            The vocabulary size of the model.
        """
        match self.model_config.model_id:
            case "fresh-xlm-roberta-base":
                return 250_002
            case "fresh-electra-small":
                return 32_000
            case _:
                raise NotImplementedError(
                    f"Vocabulary size for model {self.model_config.model_id} is not "
                    "implemented."
                )

    @cached_property
    def model_max_length(self) -> int:
        """The maximum context length of the model.

        Returns:
            The maximum context length of the model.
        """
        match self.model_config.model_id:
            case "fresh-xlm-roberta-base":
                return 512
            case "fresh-electra-small":
                return 128
            case _:
                raise NotImplementedError(
                    f"Maximum context length for model {self.model_config.model_id} is "
                    "not implemented."
                )

    @classmethod
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
        valid_models = ["fresh-electra-small", "fresh-xlm-roberta-base"]
        return model_id in valid_models

    @classmethod
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
        return ModelConfig(
            model_id=model_id,
            revision="main",
            param=None,
            task="fill-mask",
            languages=list(),
            merge=False,
            inference_backend=InferenceBackend.TRANSFORMERS,
            model_type=ModelType.ENCODER,
            fresh=True,
            model_cache_dir=create_model_cache_dir(
                cache_dir=benchmark_config.cache_dir, model_id=model_id
            ),
            adapter_base_model_id=None,
        )


def load_model_and_tokeniser(
    model_config: "ModelConfig",
    dataset_config: "DatasetConfig",
    benchmark_config: "BenchmarkConfig",
    model_max_length: int,
) -> "tuple[PreTrainedModel, PreTrainedTokenizer]":
    """Load the model and tokeniser.

    Args:
        model_config:
            The model configuration.
        dataset_config:
            The dataset configuration.
        benchmark_config:
            The benchmark configuration.
        model_max_length:
            The maximum context length of the model.

    Returns:
        The loaded model and tokeniser.
    """
    config: "PretrainedConfig"
    block_terminal_output()

    # Get the fresh model ID and the corresponding real model ID
    model_id = model_config.model_id.replace("-", "_")
    fresh_to_real_model_id_mapping = dict(
        fresh_xlm_roberta_base="FacebookAI/xlm-roberta-base",
        fresh_electra_small="google/electra-small-discriminator",
    )
    real_model_id = fresh_to_real_model_id_mapping[model_id]

    match dataset_config.task.task_group:
        case (
            TaskGroup.SEQUENCE_CLASSIFICATION
            | TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION
            | TaskGroup.SPEED
        ):
            model_cls_mapping = dict(
                fresh_xlm_roberta_base=XLMRobertaForSequenceClassification,
                fresh_electra_small=ElectraForSequenceClassification,
            )
        case TaskGroup.TOKEN_CLASSIFICATION:
            model_cls_mapping = dict(
                fresh_xlm_roberta_base=XLMRobertaForTokenClassification,
                fresh_electra_small=ElectraForTokenClassification,
            )
        case TaskGroup.QUESTION_ANSWERING:
            model_cls_mapping = dict(
                fresh_xlm_roberta_base=XLMRobertaForQuestionAnswering,
                fresh_electra_small=ElectraForQuestionAnswering,
            )
        case _:
            raise InvalidBenchmark(
                f"Task group {dataset_config.task.task_group} is not "
                f"supported for model {model_config.model_id}."
            )
    model_cls = model_cls_mapping[model_id]

    # Special case where there is a mismatch between the labels during training and
    # testing
    if dataset_config.task.task_group == TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION:
        id2label = {0: "0", 1: "1"}
    else:
        id2label = dataset_config.id2label

    config = AutoConfig.from_pretrained(
        real_model_id,
        token=get_hf_token(api_key=benchmark_config.api_key),
        num_labels=len(id2label),
        id2label=id2label,
        label2id={label: id_ for id_, label in id2label.items()},
        cache_dir=model_config.model_cache_dir,
        trust_remote_code=benchmark_config.trust_remote_code,
    )
    model = model_cls(config)

    if dataset_config.task.task_group == TaskGroup.QUESTION_ANSWERING:
        model = setup_model_for_question_answering(model=model)

    # Load the tokeniser. If the model is a subclass of a RoBERTa model then we
    # have to add a prefix space to the tokens, by the way the model is constructed
    prefix_models = ["Roberta", "GPT", "Deberta"]
    prefix = any(model_type in type(model).__name__ for model_type in prefix_models)
    try:
        tokeniser: "PreTrainedTokenizer" = AutoTokenizer.from_pretrained(
            real_model_id,
            revision=model_config.revision,
            token=get_hf_token(api_key=benchmark_config.api_key),
            add_prefix_space=prefix,
            cache_dir=model_config.model_cache_dir,
            use_fast=False if model_config.param == "slow-tokenizer" else True,
            verbose=False,
            trust_remote_code=benchmark_config.trust_remote_code,
        )
    except (JSONDecodeError, OSError) as e:
        raise InvalidModel(
            f"Could not load tokeniser for model {real_model_id!r}."
        ) from e

    model, tokeniser = align_model_and_tokeniser(
        model=model,
        tokeniser=tokeniser,
        model_max_length=model_max_length,
        raise_errors=benchmark_config.raise_errors,
    )

    return model, tokeniser
