"""All English dataset configurations used in EuroEval."""

from ..data_models import DatasetConfig
from ..languages import EN
from ..tasks import COMMON_SENSE, EUROPEAN_VALUES, KNOW, LA, MCRC, NER, RC, SENT, SUMM

### Official datasets ###

SST5_CONFIG = DatasetConfig(
    name="sst5",
    pretty_name="the truncated version of the English sentiment classification "
    "dataset SST5",
    huggingface_id="EuroEval/sst5-mini",
    task=SENT,
    languages=[EN],
)

SCALA_EN_CONFIG = DatasetConfig(
    name="scala-en",
    pretty_name="the English part of the linguistic acceptability dataset ScaLA",
    huggingface_id="EuroEval/scala-en",
    task=LA,
    languages=[EN],
)

CONLL_EN_CONFIG = DatasetConfig(
    name="conll-en",
    pretty_name="the truncated version of the English named entity recognition "
    "dataset CoNLL 2003",
    huggingface_id="EuroEval/conll-en-mini",
    task=NER,
    languages=[EN],
)

SQUAD_CONFIG = DatasetConfig(
    name="squad",
    pretty_name="the truncated version of the English question answering dataset SQuAD",
    huggingface_id="EuroEval/squad-mini",
    task=RC,
    languages=[EN],
)

CNN_DAILYMAIL_CONFIG = DatasetConfig(
    name="cnn-dailymail",
    pretty_name="the truncated version of the English summarisation dataset "
    "CNN-DailyMail",
    huggingface_id="EuroEval/cnn-dailymail-mini",
    task=SUMM,
    languages=[EN],
)

LIFE_IN_THE_UK_CONFIG = DatasetConfig(
    name="life-in-the-uk",
    pretty_name="the English knowledge dataset Life in the UK",
    huggingface_id="EuroEval/life-in-the-uk",
    task=KNOW,
    languages=[EN],
)

HELLASWAG_CONFIG = DatasetConfig(
    name="hellaswag",
    pretty_name="the truncated version of the English common-sense reasoning "
    "dataset HellaSwag",
    huggingface_id="EuroEval/hellaswag-mini",
    task=COMMON_SENSE,
    languages=[EN],
)

EUROPEAN_VALUES_EN_CONFIG = DatasetConfig(
    name="european-values-en",
    pretty_name="the English version of the European values evaluation dataset",
    huggingface_id="EuroEval/european-values-en",
    task=EUROPEAN_VALUES,
    languages=[EN],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
)


### Unofficial datasets ###

XQUAD_EN_CONFIG = DatasetConfig(
    name="xquad-en",
    pretty_name="the English version of the reading comprehension dataset XQuAD",
    huggingface_id="EuroEval/xquad-en",
    task=RC,
    languages=[EN],
    unofficial=True,
)

ARC_CONFIG = DatasetConfig(
    name="arc",
    pretty_name="the truncated version of the English knowledge dataset ARC",
    huggingface_id="EuroEval/arc-mini",
    task=KNOW,
    languages=[EN],
    unofficial=True,
)

BELEBELE_CONFIG = DatasetConfig(
    name="belebele-en",
    pretty_name="the English multiple choice reading comprehension dataset BeleBele",
    huggingface_id="EuroEval/belebele-mini",
    task=MCRC,
    languages=[EN],
    unofficial=True,
)

MMLU_CONFIG = DatasetConfig(
    name="mmlu",
    pretty_name="the truncated version of the English knowledge dataset MMLU",
    huggingface_id="EuroEval/mmlu-mini",
    task=KNOW,
    languages=[EN],
    unofficial=True,
)

MULTI_WIKI_QA_EN_CONFIG = DatasetConfig(
    name="multi-wiki-qa-en",
    pretty_name="the truncated version of the English part of the reading "
    "comprehension dataset MultiWikiQA",
    huggingface_id="EuroEval/multi-wiki-qa-en-mini",
    task=RC,
    languages=[EN],
    unofficial=True,
)

WINOGRANDE_CONFIG = DatasetConfig(
    name="winogrande",
    pretty_name="the English common-sense reasoning dataset Winogrande",
    huggingface_id="EuroEval/winogrande-en",
    task=COMMON_SENSE,
    languages=[EN],
    _labels=["a", "b"],
    unofficial=True,
)

EUROPEAN_VALUES_SITUATIONAL_EN_CONFIG = DatasetConfig(
    name="european-values-situational-en",
    pretty_name="the English version of the European values evaluation dataset, where "
    "the questions are phrased in a situational way",
    huggingface_id="EuroEval/european-values-situational-en",
    task=EUROPEAN_VALUES,
    languages=[EN],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)

EUROPEAN_VALUES_COMPLETIONS_EN_CONFIG = DatasetConfig(
    name="european-values-completions-en",
    pretty_name="the English version of the European values evaluation dataset, where "
    "the questions are phrased as sentence completions",
    huggingface_id="EuroEval/european-values-completions-en",
    task=EUROPEAN_VALUES,
    languages=[EN],
    splits=["test"],
    bootstrap_samples=False,
    _instruction_prompt="{text}",
    unofficial=True,
)
