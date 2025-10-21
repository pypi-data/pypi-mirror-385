"""Constants used throughout the project."""

from typing import TypeVar

from .enums import TaskGroup

# Type variable used for generic typing
T = TypeVar("T", bound=object)


# This is used as input to generative models; it cannot be a special token
DUMMY_FILL_VALUE = 100


# This is the maximum allowed context length for models for the purpose of this
# benchmark. We will still report the models' true maximum context length in the
# metadata, but we won't use it for evaluation, as vLLM needs to allocate memory for
# all tokens in the context.
MAX_CONTEXT_LENGTH = 8_192


# We need to raise the amount of tokens generated for reasoning models, to give them
# time to think
REASONING_MAX_TOKENS = 8_192


# The Hugging Face Hub pipeline tags used to classify models as generative
GENERATIVE_PIPELINE_TAGS = [
    "text-generation",
    "text2text-generation",
    "image-text-to-text",
    "audio-text-to-text",
    "video-text-to-text",
]


# Used to disallow non-generative models to be evaluated on these task groups
GENERATIVE_DATASET_TASK_GROUPS = [TaskGroup.TEXT_TO_TEXT]


# Local models are required to have these files in their directory
LOCAL_MODELS_REQUIRED_FILES = ["config.json"]


# The number of top log probabilities to return for generative models. For several APIs
# this is the maximum number of log probabilities that can be returned
MAX_VLLM_LOGPROBS = 20
MAX_LITELLM_LOGPROBS = 8


# We make sure to remove these metric attributes after each iteration, to avoid memory
# leaks
METRIC_ATTRIBUTES_TAKING_UP_MEMORY = ["cached_bertscorer"]


# Hugging Face Hub tags used to classify models as merge models
MERGE_TAGS = ["merge", "mergekit"]


# The minimum required CUDA compute capability for using bfloat16 in vLLM
VLLM_BF16_MIN_CUDA_COMPUTE_CAPABILITY = 8.0


# Used to detect whether a model is a reasoning model
REASONING_TOKENS = [
    ("<think>", "</think>"),
    ("<reason>", "</reason>"),
    ("<reasoning>", "</reasoning>"),
]


# These tokens are sometimes used by models to indicate the end of a generated
# response, but they do not use them as a proper EOS token, so we have to deal with them
# manually. We only use them as stop tokens if they actually appear in the model's
# output
CUSTOM_STOP_TOKENS = ["<sep>"]


# For classification tasks we force LiteLLM models to output a JSON dictionary with a
# single key and the values being restricted to the allowed labels. This is the key we
# use
LITELLM_CLASSIFICATION_OUTPUT_KEY = "label"


# These characters are stripped from JSON output when trying to identify the label
JSON_STRIP_CHARACTERS = ' {}\n\r":'


# The number of tokens we generate when evaluating generative models on classification
# tasks. We also use this to determine whether we should store logprobs in the model
# outputs (and cache).
NUM_GENERATION_TOKENS_FOR_CLASSIFICATION = 10
