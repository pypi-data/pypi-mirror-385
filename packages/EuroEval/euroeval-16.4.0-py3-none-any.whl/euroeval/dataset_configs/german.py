"""All German dataset configurations used in EuroEval."""

from ..data_models import DatasetConfig
from ..languages import DE
from ..tasks import COMMON_SENSE, EUROPEAN_VALUES, KNOW, LA, MCRC, NER, RC, SENT, SUMM

### Official datasets ###

SB10K_CONFIG = DatasetConfig(
    name="sb10k",
    pretty_name="the truncated version of the German sentiment classification "
    "dataset SB10k",
    huggingface_id="EuroEval/sb10k-mini",
    task=SENT,
    languages=[DE],
)

SCALA_DE_CONFIG = DatasetConfig(
    name="scala-de",
    pretty_name="the German part of the linguistic acceptability dataset ScaLA",
    huggingface_id="EuroEval/scala-de",
    task=LA,
    languages=[DE],
)

GERMEVAL_CONFIG = DatasetConfig(
    name="germeval",
    pretty_name="the truncated version of the German named entity recognition "
    "dataset GermEval",
    huggingface_id="EuroEval/germeval-mini",
    task=NER,
    languages=[DE],
)

GERMANQUAD_CONFIG = DatasetConfig(
    name="germanquad",
    pretty_name="the truncated version of the German reading comprehension dataset "
    "GermanQuAD",
    huggingface_id="EuroEval/germanquad-mini",
    task=RC,
    languages=[DE],
)

MLSUM_DE_CONFIG = DatasetConfig(
    name="mlsum-de",
    pretty_name="the truncated version of the German summarisation dataset MLSum-de",
    huggingface_id="EuroEval/mlsum-mini",
    task=SUMM,
    languages=[DE],
)

MMLU_DE_CONFIG = DatasetConfig(
    name="mmlu-de",
    pretty_name="the truncated version of the German knowledge dataset MMLU-de, "
    "translated from the English MMLU dataset",
    huggingface_id="EuroEval/mmlu-de-mini",
    task=KNOW,
    languages=[DE],
)

HELLASWAG_DE_CONFIG = DatasetConfig(
    name="hellaswag-de",
    pretty_name="the truncated version of the German common-sense reasoning dataset "
    "HellaSwag-de, translated from the English HellaSwag dataset",
    huggingface_id="EuroEval/hellaswag-de-mini",
    task=COMMON_SENSE,
    languages=[DE],
)

EUROPEAN_VALUES_DE_CONFIG = DatasetConfig(
    name="european-values-de",
    pretty_name="the German version of the European values evaluation dataset",
    huggingface_id="EuroEval/european-values-de",
    task=EUROPEAN_VALUES,
    languages=[DE],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
)


### Unofficial datasets ###

XQUAD_DE_CONFIG = DatasetConfig(
    name="xquad-de",
    pretty_name="the German version of the reading comprehension dataset XQuAD",
    huggingface_id="EuroEval/xquad-de",
    task=RC,
    languages=[DE],
    unofficial=True,
)

ARC_DE_CONFIG = DatasetConfig(
    name="arc-de",
    pretty_name="the truncated version of the German knowledge dataset ARC-de, "
    "translated from the English ARC dataset",
    huggingface_id="EuroEval/arc-de-mini",
    task=KNOW,
    languages=[DE],
    unofficial=True,
)

BELEBELE_DE_CONFIG = DatasetConfig(
    name="belebele-de",
    pretty_name="the German multiple choice reading comprehension dataset BeleBele-de, "
    "translated from the English BeleBele dataset",
    huggingface_id="EuroEval/belebele-de-mini",
    task=MCRC,
    languages=[DE],
    unofficial=True,
)

MULTI_WIKI_QA_DE_CONFIG = DatasetConfig(
    name="multi-wiki-qa-de",
    pretty_name="the truncated version of the German part of the reading "
    "comprehension dataset MultiWikiQA",
    huggingface_id="EuroEval/multi-wiki-qa-de-mini",
    task=RC,
    languages=[DE],
    unofficial=True,
)

GOLDENSWAG_DE_CONFIG = DatasetConfig(
    name="goldenswag-de",
    pretty_name="the truncated version of the German common-sense reasoning "
    "dataset GoldenSwag-de, translated from the English GoldenSwag dataset",
    huggingface_id="EuroEval/goldenswag-de-mini",
    task=COMMON_SENSE,
    languages=[DE],
    unofficial=True,
)

WINOGRANDE_DE_CONFIG = DatasetConfig(
    name="winogrande-de",
    pretty_name="the German common-sense reasoning dataset Winogrande-de, translated "
    "from the English Winogrande dataset",
    huggingface_id="EuroEval/winogrande-de",
    task=COMMON_SENSE,
    languages=[DE],
    _labels=["a", "b"],
    unofficial=True,
)

EUROPEAN_VALUES_SITUATIONAL_DE_CONFIG = DatasetConfig(
    name="european-values-situational-de",
    pretty_name="the German version of the European values evaluation dataset, where "
    "the questions are phrased in a situational way",
    huggingface_id="EuroEval/european-values-situational-de",
    task=EUROPEAN_VALUES,
    languages=[DE],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)

EUROPEAN_VALUES_COMPLETIONS_DE_CONFIG = DatasetConfig(
    name="european-values-completions-de",
    pretty_name="the German version of the European values evaluation dataset, where "
    "the questions are phrased as sentence completions",
    huggingface_id="EuroEval/european-values-completions-de",
    task=EUROPEAN_VALUES,
    languages=[DE],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)
