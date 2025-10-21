# /// script
# requires-python = ">=3.10,<4.0"
# dependencies = [
#     "datasets==3.5.0",
#     "huggingface-hub==0.24.0",
#     "pandas==2.2.0",
#     "requests==2.32.3",
# ]
# ///

"""Create the Finnish version of the XLSum summarisation dataset."""

import pandas as pd
from constants import MAX_NUM_CHARS_IN_ARTICLE, MIN_NUM_CHARS_IN_ARTICLE
from datasets import Dataset, DatasetDict, Split, load_dataset
from huggingface_hub import HfApi


def main() -> None:
    """Create the Finnish XL-Sum dataset and upload to HF Hub."""
    dataset_id = "TurkuNLP/xlsum-fi"

    dataset = load_dataset(dataset_id, trust_remote_code=True, token=True)
    assert isinstance(dataset, DatasetDict)

    dataset = dataset.rename_columns(column_mapping=dict(summary="target_text"))

    train_df = dataset["train"].to_pandas()
    val_df = dataset["validation"].to_pandas()
    test_df = dataset["test"].to_pandas()
    assert isinstance(train_df, pd.DataFrame)
    assert isinstance(val_df, pd.DataFrame)
    assert isinstance(test_df, pd.DataFrame)

    # Only work with samples where the text is not very large or small
    train_lengths = train_df.text.str.len()
    val_lengths = val_df.text.str.len()
    test_lengths = test_df.text.str.len()
    lower_bound = MIN_NUM_CHARS_IN_ARTICLE
    upper_bound = MAX_NUM_CHARS_IN_ARTICLE
    train_df = train_df[train_lengths.between(lower_bound, upper_bound)]
    val_df = val_df[val_lengths.between(lower_bound, upper_bound)]
    test_df = test_df[test_lengths.between(lower_bound, upper_bound)]

    # Create test split
    test_size = 2048
    val_samples_to_test = val_df.sample(n=test_size - len(test_df), random_state=4242)
    # Remove the samples from the validation set
    val_df = val_df[~val_df.index.isin(val_samples_to_test.index)]
    # Concatenate the test set with the sampled validation set
    test_df = pd.concat([test_df, val_samples_to_test])

    # Create validation split
    val_size = 256
    val_df = val_df.sample(n=val_size, random_state=4242)

    # Create train split
    train_size = 1024
    train_df = train_df.sample(n=train_size, random_state=4242)

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
    dataset_id = "EuroEval/xlsum-fi-mini"
    HfApi().delete_repo(dataset_id, repo_type="dataset", missing_ok=True)
    dataset.push_to_hub(dataset_id, private=True)


if __name__ == "__main__":
    main()
