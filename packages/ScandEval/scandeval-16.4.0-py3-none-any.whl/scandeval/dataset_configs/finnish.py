"""All Finnish dataset configurations used in EuroEval."""

from ..data_models import DatasetConfig
from ..languages import FI
from ..tasks import COMMON_SENSE, EUROPEAN_VALUES, LA, MCRC, NER, RC, SENT, SUMM

### Official datasets ###

SCANDISENT_FI_CONFIG = DatasetConfig(
    name="scandisent-fi",
    pretty_name="the truncated version of the Finnish part of the binary sentiment "
    "classification dataset ScandiSent",
    huggingface_id="EuroEval/scandisent-fi-mini",
    task=SENT,
    languages=[FI],
    _labels=["negative", "positive"],
)

TURKU_NER_FI_CONFIG = DatasetConfig(
    name="turku-ner-fi",
    pretty_name="the Finnish part of the named entity recognition dataset Turku NER",
    huggingface_id="EuroEval/turku-ner-fi-mini",
    task=NER,
    languages=[FI],
)

TYDIQA_FI_CONFIG = DatasetConfig(
    name="tydiqa-fi",
    pretty_name="the Finnish part of the TydiQA reading comprehension dataset",
    huggingface_id="EuroEval/tydiqa-fi-mini",
    task=RC,
    languages=[FI],
)

XLSUM_FI_CONFIG = DatasetConfig(
    name="xlsum-fi",
    pretty_name="the Finnish summarisation dataset XL-Sum",
    huggingface_id="EuroEval/xlsum-fi-mini",
    task=SUMM,
    languages=[FI],
)

HELLASWAG_FI_CONFIG = DatasetConfig(
    name="hellaswag-fi",
    pretty_name="the truncated version of the Finnish common-sense reasoning dataset "
    "HellaSwag-fi, translated from the English HellaSwag dataset",
    huggingface_id="EuroEval/hellaswag-fi-mini",
    task=COMMON_SENSE,
    languages=[FI],
)

SCALA_FI_CONFIG = DatasetConfig(
    name="scala-fi",
    pretty_name="the Finnish part of the linguistic acceptability dataset ScaLA",
    huggingface_id="EuroEval/scala-fi",
    task=LA,
    languages=[FI],
)

EUROPEAN_VALUES_FI_CONFIG = DatasetConfig(
    name="european-values-fi",
    pretty_name="the Finnish version of the European values evaluation dataset",
    huggingface_id="EuroEval/european-values-fi",
    task=EUROPEAN_VALUES,
    languages=[FI],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
)


### Unofficial datasets ###

BELEBELE_FI_CONFIG = DatasetConfig(
    name="belebele-fi",
    pretty_name="the Finnish multiple choice reading comprehension dataset "
    "BeleBele-fi, translated from the English BeleBele dataset",
    huggingface_id="EuroEval/belebele-fi-mini",
    task=MCRC,
    languages=[FI],
    unofficial=True,
)

MULTI_WIKI_QA_FI_CONFIG = DatasetConfig(
    name="multi-wiki-qa-fi",
    pretty_name="the truncated version of the Finnish part of the reading "
    "comprehension dataset MultiWikiQA",
    huggingface_id="EuroEval/multi-wiki-qa-fi-mini",
    task=RC,
    languages=[FI],
    unofficial=True,
)

GOLDENSWAG_FI_CONFIG = DatasetConfig(
    name="goldenswag-fi",
    pretty_name="the truncated version of the Finnish common-sense reasoning "
    "dataset GoldenSwag-fi, translated from the English GoldenSwag dataset",
    huggingface_id="EuroEval/goldenswag-fi-mini",
    task=COMMON_SENSE,
    languages=[FI],
    unofficial=True,
)

WINOGRANDE_FI_CONFIG = DatasetConfig(
    name="winogrande-fi",
    pretty_name="the Finnish common-sense reasoning dataset Winogrande-fi, translated "
    "from the English Winogrande dataset",
    huggingface_id="EuroEval/winogrande-fi",
    task=COMMON_SENSE,
    languages=[FI],
    _labels=["a", "b"],
    unofficial=True,
)

EUROPEAN_VALUES_SITUATIONAL_FI_CONFIG = DatasetConfig(
    name="european-values-situational-fi",
    pretty_name="the Finnish version of the European values evaluation dataset, where "
    "the questions are phrased in a situational way",
    huggingface_id="EuroEval/european-values-situational-fi",
    task=EUROPEAN_VALUES,
    languages=[FI],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)

EUROPEAN_VALUES_COMPLETIONS_FI_CONFIG = DatasetConfig(
    name="european-values-completions-fi",
    pretty_name="the Finnish version of the European values evaluation dataset, where "
    "the questions are phrased as sentence completions",
    huggingface_id="EuroEval/european-values-completions-fi",
    task=EUROPEAN_VALUES,
    languages=[FI],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)
