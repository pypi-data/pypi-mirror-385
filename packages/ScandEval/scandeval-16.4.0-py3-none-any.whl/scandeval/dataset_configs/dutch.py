"""All Dutch dataset configurations used in EuroEval."""

from ..data_models import DatasetConfig
from ..languages import NL
from ..tasks import COMMON_SENSE, EUROPEAN_VALUES, KNOW, LA, MCRC, NER, RC, SENT, SUMM

### Official datasets ###

DBRD_CONFIG = DatasetConfig(
    name="dbrd",
    pretty_name="the truncated version of the Dutch sentiment classification "
    "dataset DBRD",
    huggingface_id="EuroEval/dbrd-mini",
    task=SENT,
    languages=[NL],
    _labels=["negative", "positive"],
)

SCALA_NL_CONFIG = DatasetConfig(
    name="scala-nl",
    pretty_name="the Dutch part of the linguistic acceptability dataset ScaLA",
    huggingface_id="EuroEval/scala-nl",
    task=LA,
    languages=[NL],
)

CONLL_NL_CONFIG = DatasetConfig(
    name="conll-nl",
    pretty_name="the Dutch part of the truncated version of the named entity "
    "recognition dataset CoNLL 2002",
    huggingface_id="EuroEval/conll-nl-mini",
    task=NER,
    languages=[NL],
)

SQUAD_NL_CONFIG = DatasetConfig(
    name="squad-nl",
    pretty_name="the truncated version of the Dutch reading comprehension dataset "
    "SQuAD-nl, translated from the English SQuAD dataset",
    huggingface_id="EuroEval/squad-nl-v2-mini",
    task=RC,
    languages=[NL],
)

WIKI_LINGUA_NL_CONFIG = DatasetConfig(
    name="wiki-lingua-nl",
    pretty_name="the Dutch part of the truncated version of the summarisation dataset "
    "WikiLingua",
    huggingface_id="EuroEval/wiki-lingua-nl-mini",
    task=SUMM,
    languages=[NL],
)

MMLU_NL_CONFIG = DatasetConfig(
    name="mmlu-nl",
    pretty_name="the truncated version of the Dutch knowledge dataset MMLU-nl, "
    "translated from the English MMLU dataset",
    huggingface_id="EuroEval/mmlu-nl-mini",
    task=KNOW,
    languages=[NL],
)

HELLASWAG_NL_CONFIG = DatasetConfig(
    name="hellaswag-nl",
    pretty_name="the truncated version of the Dutch common-sense reasoning dataset "
    "HellaSwag-nl, translated from the English HellaSwag dataset",
    huggingface_id="EuroEval/hellaswag-nl-mini",
    task=COMMON_SENSE,
    languages=[NL],
)

EUROPEAN_VALUES_NL_CONFIG = DatasetConfig(
    name="european-values-nl",
    pretty_name="the Dutch version of the European values evaluation dataset",
    huggingface_id="EuroEval/european-values-nl",
    task=EUROPEAN_VALUES,
    languages=[NL],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
)


### Unofficial datasets ###

DUTCH_COLA_CONFIG = DatasetConfig(
    name="dutch-cola",
    pretty_name="the truncated version of the Dutch linguistic acceptability dataset "
    "Dutch CoLA",
    huggingface_id="EuroEval/dutch-cola",
    task=LA,
    languages=[NL],
    unofficial=True,
)

DUTCH_COLA_FULL_CONFIG = DatasetConfig(
    name="dutch-cola-full",
    pretty_name="the Dutch linguistic acceptability dataset Dutch CoLA",
    huggingface_id="EuroEval/dutch-cola-full",
    task=LA,
    languages=[NL],
    unofficial=True,
)

ARC_NL_CONFIG = DatasetConfig(
    name="arc-nl",
    pretty_name="the truncated version of the Dutch knowledge dataset ARC-nl, "
    "translated from the English ARC dataset",
    huggingface_id="EuroEval/arc-nl-mini",
    task=KNOW,
    languages=[NL],
    unofficial=True,
)

BELEBELE_NL_CONFIG = DatasetConfig(
    name="belebele-nl",
    pretty_name="the Dutch multiple choice reading comprehension dataset BeleBele-nl, "
    "translated from the English BeleBele dataset",
    huggingface_id="EuroEval/belebele-nl-mini",
    task=MCRC,
    languages=[NL],
    unofficial=True,
)

MULTI_WIKI_QA_NL_CONFIG = DatasetConfig(
    name="multi-wiki-qa-nl",
    pretty_name="the truncated version of the Dutch part of the reading "
    "comprehension dataset MultiWikiQA",
    huggingface_id="EuroEval/multi-wiki-qa-nl-mini",
    task=RC,
    languages=[NL],
    unofficial=True,
)

GOLDENSWAG_NL_CONFIG = DatasetConfig(
    name="goldenswag-nl",
    pretty_name="the truncated version of the Dutch common-sense reasoning "
    "dataset GoldenSwag-nl, translated from the English GoldenSwag dataset",
    huggingface_id="EuroEval/goldenswag-nl-mini",
    task=COMMON_SENSE,
    languages=[NL],
    unofficial=True,
)

WINOGRANDE_NL_CONFIG = DatasetConfig(
    name="winogrande-nl",
    pretty_name="the Dutch common-sense reasoning dataset Winogrande-nl, translated "
    "from the English Winogrande dataset",
    huggingface_id="EuroEval/winogrande-nl",
    task=COMMON_SENSE,
    languages=[NL],
    _labels=["a", "b"],
    unofficial=True,
)

EUROPEAN_VALUES_SITUATIONAL_NL_CONFIG = DatasetConfig(
    name="european-values-situational-nl",
    pretty_name="the Dutch version of the European values evaluation dataset, where "
    "the questions are phrased in a situational way",
    huggingface_id="EuroEval/european-values-situational-nl",
    task=EUROPEAN_VALUES,
    languages=[NL],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)

EUROPEAN_VALUES_COMPLETIONS_NL_CONFIG = DatasetConfig(
    name="european-values-completions-nl",
    pretty_name="the Dutch version of the European values evaluation dataset, where "
    "the questions are phrased as sentence completions",
    huggingface_id="EuroEval/european-values-completions-nl",
    task=EUROPEAN_VALUES,
    languages=[NL],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)
