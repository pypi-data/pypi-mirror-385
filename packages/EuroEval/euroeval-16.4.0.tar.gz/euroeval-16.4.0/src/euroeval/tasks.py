"""All benchmarks tasks used in EuroEval."""

from . import metrics as m
from .constants import NUM_GENERATION_TOKENS_FOR_CLASSIFICATION
from .data_models import Task
from .enums import GenerativeType, ModelType, TaskGroup
from .prompt_templates import (
    LA_TEMPLATES,
    MULTIPLE_CHOICE_TEMPLATES,
    NER_TEMPLATES,
    RC_TEMPLATES,
    SENT_TEMPLATES,
    SUMM_TEMPLATES,
)


def get_all_tasks() -> dict[str, Task]:
    """Get a list of all the dataset tasks.

    Returns:
        A mapping between names of dataset tasks and their configurations.
    """
    return {cfg.name: cfg for cfg in globals().values() if isinstance(cfg, Task)}


LA = Task(
    name="linguistic-acceptability",
    task_group=TaskGroup.SEQUENCE_CLASSIFICATION,
    template_dict=LA_TEMPLATES,
    metrics=[m.mcc_metric, m.macro_f1_metric],
    default_num_few_shot_examples=12,
    default_max_generated_tokens=NUM_GENERATION_TOKENS_FOR_CLASSIFICATION,
    default_labels=["correct", "incorrect"],
    uses_logprobs=True,
)


NER = Task(
    name="named-entity-recognition",
    task_group=TaskGroup.TOKEN_CLASSIFICATION,
    template_dict=NER_TEMPLATES,
    metrics=[m.micro_f1_no_misc_metric, m.micro_f1_metric],
    default_num_few_shot_examples=8,
    default_max_generated_tokens=128,
    default_labels=[
        "o",
        "b-loc",
        "i-loc",
        "b-org",
        "i-org",
        "b-per",
        "i-per",
        "b-misc",
        "i-misc",
    ],
    uses_structured_output=True,
)


RC = Task(
    name="reading-comprehension",
    task_group=TaskGroup.QUESTION_ANSWERING,
    template_dict=RC_TEMPLATES,
    metrics=[m.f1_metric, m.em_metric],
    default_num_few_shot_examples=4,
    default_max_generated_tokens=32,
    default_labels=["start_positions", "end_positions"],
)


SENT = Task(
    name="sentiment-classification",
    task_group=TaskGroup.SEQUENCE_CLASSIFICATION,
    template_dict=SENT_TEMPLATES,
    metrics=[m.mcc_metric, m.macro_f1_metric],
    default_num_few_shot_examples=12,
    default_max_generated_tokens=NUM_GENERATION_TOKENS_FOR_CLASSIFICATION,
    default_labels=["positive", "neutral", "negative"],
    uses_logprobs=True,
)


SUMM = Task(
    name="summarization",
    task_group=TaskGroup.TEXT_TO_TEXT,
    template_dict=SUMM_TEMPLATES,
    metrics=[m.bert_score_metric, m.rouge_l_metric],
    default_num_few_shot_examples=1,
    default_max_generated_tokens=256,
    default_labels=[],
    default_allowed_model_types=[ModelType.GENERATIVE],
)


KNOW = Task(
    name="knowledge",
    task_group=TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION,
    template_dict=MULTIPLE_CHOICE_TEMPLATES,
    metrics=[m.mcc_metric, m.accuracy_metric],
    default_num_few_shot_examples=5,
    default_max_generated_tokens=NUM_GENERATION_TOKENS_FOR_CLASSIFICATION,
    default_labels=["a", "b", "c", "d"],
    default_allowed_model_types=[ModelType.GENERATIVE],
    uses_logprobs=True,
)


MCRC = Task(
    name="multiple-choice-reading-comprehension",
    task_group=TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION,
    template_dict=MULTIPLE_CHOICE_TEMPLATES,
    metrics=[m.mcc_metric, m.accuracy_metric],
    default_num_few_shot_examples=5,
    default_max_generated_tokens=NUM_GENERATION_TOKENS_FOR_CLASSIFICATION,
    default_labels=["a", "b", "c", "d"],
    default_allowed_model_types=[ModelType.GENERATIVE],
    uses_logprobs=True,
)


COMMON_SENSE = Task(
    name="common-sense-reasoning",
    task_group=TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION,
    template_dict=MULTIPLE_CHOICE_TEMPLATES,
    metrics=[m.mcc_metric, m.accuracy_metric],
    default_num_few_shot_examples=5,
    default_max_generated_tokens=NUM_GENERATION_TOKENS_FOR_CLASSIFICATION,
    default_labels=["a", "b", "c", "d"],
    default_allowed_model_types=[ModelType.GENERATIVE],
    uses_logprobs=True,
)


EUROPEAN_VALUES = Task(
    name="european-values",
    task_group=TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION,
    template_dict=MULTIPLE_CHOICE_TEMPLATES,
    metrics=[m.european_values_metric],
    default_num_few_shot_examples=0,
    default_max_generated_tokens=NUM_GENERATION_TOKENS_FOR_CLASSIFICATION,
    default_labels=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"],
    default_allowed_model_types=[ModelType.GENERATIVE],
    default_allowed_generative_types=[
        GenerativeType.INSTRUCTION_TUNED,
        GenerativeType.REASONING,
    ],
    requires_zero_shot=True,
    uses_logprobs=True,
    default_allow_invalid_model_outputs=False,
)


SPEED = Task(
    name="speed",
    task_group=TaskGroup.SPEED,
    template_dict={},
    metrics=[m.speed_metric, m.speed_short_metric],
    default_num_few_shot_examples=0,
    default_max_generated_tokens=5,
    default_labels=[],
)
