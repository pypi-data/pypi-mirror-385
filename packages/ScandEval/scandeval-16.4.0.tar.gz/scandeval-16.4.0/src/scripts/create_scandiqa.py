# /// script
# requires-python = ">=3.10,<4.0"
# dependencies = [
#     "datasets==3.5.0",
#     "huggingface-hub==0.24.0",
#     "pandas==2.2.0",
#     "requests==2.32.3",
# ]
# ///

"""Create the ScandiQA-mini datasets and upload them to the HF Hub."""

import pandas as pd
from constants import (
    MAX_NUM_CHARS_IN_CONTEXT,
    MAX_NUM_CHARS_IN_QUESTION,
    MIN_NUM_CHARS_IN_CONTEXT,
    MIN_NUM_CHARS_IN_QUESTION,
)
from datasets.arrow_dataset import Dataset
from datasets.combine import concatenate_datasets
from datasets.dataset_dict import DatasetDict
from datasets.load import load_dataset
from datasets.splits import Split
from huggingface_hub.hf_api import HfApi


def main() -> None:
    """Create the ScandiQA-mini datasets and upload them to the HF Hub."""
    dataset_id = "alexandrainst/scandi-qa"

    # Iterate over the Danish, Norwegian and Swedish languages
    for language in ["da", "no", "sv"]:
        # Load the datasets from the `alexandrainst` organisation
        train = load_dataset(dataset_id, language, split="train", token=True)
        val = load_dataset(dataset_id, language, split="val", token=True)
        test = load_dataset(dataset_id, language, split="test", token=True)

        # Ensure that the datasets are indeed datasets
        assert isinstance(train, Dataset)
        assert isinstance(val, Dataset)
        assert isinstance(test, Dataset)

        # Merge the splits
        df = concatenate_datasets([train, val, test]).to_pandas()

        # Ensure that `df` is indeed a Pandas DataFrame
        assert isinstance(df, pd.DataFrame)

        # Only work with samples where the context is not very large or small
        lengths = df.context.str.len()
        df = df[lengths.between(MIN_NUM_CHARS_IN_CONTEXT, MAX_NUM_CHARS_IN_CONTEXT)]

        # Only work with samples where the context is not very large or small
        lengths = df.question.str.len()
        df_with_no_outliers = df[
            lengths.between(MIN_NUM_CHARS_IN_QUESTION, MAX_NUM_CHARS_IN_QUESTION)
        ]

        # Only work with the questions having answers in the context
        has_answer: pd.Series = df_with_no_outliers.answers.map(
            lambda dct: dct["text"][0] != ""
        )
        df_with_answer: pd.DataFrame = df_with_no_outliers.loc[has_answer]

        # Create validation split
        val_size = 256
        val_df = df_with_answer.sample(n=val_size, random_state=4242)

        # Create test split
        test_size = 2048
        df_with_answer_filtered: pd.DataFrame = df_with_answer.loc[
            ~df_with_answer.index.isin(val_df.index)
        ]
        test_df = df_with_answer_filtered.sample(n=test_size, random_state=4242)

        # Create train split
        train_size = 1024
        full_train_df_with_answer = df_with_answer_filtered.loc[
            ~df_with_answer_filtered.index.isin(test_df.index)
        ]
        train_df = full_train_df_with_answer.sample(n=train_size, random_state=4242)

        val_df = val_df.reset_index(drop=True)
        test_df = test_df.reset_index(drop=True)
        train_df = train_df.reset_index(drop=True)

        # Collect datasets in a dataset dictionary
        dataset = DatasetDict(
            train=Dataset.from_pandas(train_df, split=Split.TRAIN),
            val=Dataset.from_pandas(val_df, split=Split.VALIDATION),
            test=Dataset.from_pandas(test_df, split=Split.TEST),
        )

        # Push the dataset to the Hugging Face Hub
        dataset_id = f"EuroEval/scandiqa-{language}-mini"
        HfApi().delete_repo(dataset_id, repo_type="dataset", missing_ok=True)
        dataset.push_to_hub(dataset_id, private=True)


if __name__ == "__main__":
    main()
