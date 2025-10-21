"""All Faroese dataset configurations used in EuroEval."""

from ..data_models import DatasetConfig
from ..languages import FO
from ..tasks import LA, NER, RC, SENT

### Official datasets ###

FOSENT_CONFIG = DatasetConfig(
    name="fosent",
    pretty_name="the Faroese sentiment classification dataset FoSent",
    huggingface_id="EuroEval/fosent",
    task=SENT,
    languages=[FO],
    _num_few_shot_examples=5,
)

SCALA_FO_CONFIG = DatasetConfig(
    name="scala-fo",
    pretty_name="the Faroese part of the linguistic acceptability dataset ScaLA",
    huggingface_id="EuroEval/scala-fo",
    task=LA,
    languages=[FO],
)

FONE_CONFIG = DatasetConfig(
    name="fone",
    pretty_name="the truncated version of the Faroese named entity recognition "
    "dataset FoNE",
    huggingface_id="EuroEval/fone-mini",
    task=NER,
    languages=[FO],
)

FOQA_CONFIG = DatasetConfig(
    name="foqa",
    pretty_name="the Faroese reading comprehension dataset FoQA",
    huggingface_id="EuroEval/foqa",
    task=RC,
    languages=[FO],
)

# TODO: No Faroese version of the European values dataset exists yet
# EUROPEAN_VALUES_FO_CONFIG = DatasetConfig(
#     name="european-values-fo",
#     pretty_name="the Faroese version of the European values evaluation dataset",
#     huggingface_id="EuroEval/european-values-fo",
#     task=EUROPEAN_VALUES,
#     languages=[FO],
#     splits=["test"],
#     bootstrap_samples=False,
#     _instruction_prompt="{text}",
# )
#
# EUROPEAN_VALUES_SITUATIONAL_FO_CONFIG = DatasetConfig(
#     name="european-values-situational-fo",
#     pretty_name="the Faroese version of the European values evaluation dataset, "
#     "where the questions are phrased in a situational way",
#     huggingface_id="EuroEval/european-values-situational-fo",
#     task=EUROPEAN_VALUES,
#     languages=[FO],
#     splits=["test"],
#     bootstrap_samples=False,
#     _instruction_prompt="{text}",
#     unofficial=True,
# )
#
# EUROPEAN_VALUES_COMPLETIONS_FO_CONFIG = DatasetConfig(
#     name="european-values-completions-fo",
#     pretty_name="the Faroese version of the European values evaluation dataset, "
#     "where the questions are phrased as sentence completions",
#     huggingface_id="EuroEval/european-values-completions-fo",
#     task=EUROPEAN_VALUES,
#     languages=[FO],
#     splits=["test"],
#     bootstrap_samples=False,
#     _instruction_prompt="{text}",
#     unofficial=True,
# )


### Unofficial datasets ###

WIKIANN_FO_CONFIG = DatasetConfig(
    name="wikiann-fo",
    pretty_name="the truncated version of the Faroese part of the named entity "
    "recognition dataset WikiANN",
    huggingface_id="EuroEval/wikiann-fo-mini",
    task=NER,
    languages=[FO],
    unofficial=True,
)

MULTI_WIKI_QA_FO_CONFIG = DatasetConfig(
    name="multi-wiki-qa-fo",
    pretty_name="the truncated version of the Faroese part of the reading "
    "comprehension dataset MultiWikiQA",
    huggingface_id="EuroEval/multi-wiki-qa-fo-mini",
    task=RC,
    languages=[FO],
    unofficial=True,
)
