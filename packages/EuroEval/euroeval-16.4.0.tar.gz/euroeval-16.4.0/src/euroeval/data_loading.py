"""Functions related to the loading of the data."""

import logging
import sys
import time
import typing as t

import requests
from datasets import DatasetDict, load_dataset
from datasets.exceptions import DatasetsError
from huggingface_hub.errors import HfHubHTTPError
from numpy.random import Generator

from .exceptions import HuggingFaceHubDown, InvalidBenchmark
from .logging_utils import log, no_terminal_output
from .tasks import EUROPEAN_VALUES
from .utils import unscramble

if t.TYPE_CHECKING:
    from datasets import Dataset

    from .data_models import BenchmarkConfig, DatasetConfig


def load_data(
    rng: Generator, dataset_config: "DatasetConfig", benchmark_config: "BenchmarkConfig"
) -> list["DatasetDict"]:
    """Load the raw bootstrapped datasets.

    Args:
        rng:
            The random number generator to use.
        dataset_config:
            The configuration for the dataset.
        benchmark_config:
            The configuration for the benchmark.

    Returns:
        A list of bootstrapped datasets, one for each iteration.

    Raises:
        InvalidBenchmark:
            If the dataset cannot be loaded.
        HuggingFaceHubDown:
            If the Hugging Face Hub is down.
    """
    dataset = load_raw_data(
        dataset_config=dataset_config, cache_dir=benchmark_config.cache_dir
    )

    if not benchmark_config.evaluate_test_split and "val" in dataset:
        dataset["test"] = dataset["val"]

    # Remove empty examples from the datasets
    for text_feature in ["tokens", "text"]:
        for split in dataset_config.splits:
            if text_feature in dataset[split].features:
                dataset = dataset.filter(lambda x: len(x[text_feature]) > 0)

    # If we are testing then truncate the test set, unless we need the full set for
    # evaluation
    if hasattr(sys, "_called_from_test") and dataset_config.task != EUROPEAN_VALUES:
        dataset["test"] = dataset["test"].select(range(1))

    # Bootstrap the splits, if applicable
    if dataset_config.bootstrap_samples:
        bootstrapped_splits: dict[str, list["Dataset"]] = dict()
        for split in dataset_config.splits:
            bootstrap_indices = rng.integers(
                0,
                len(dataset[split]),
                size=(benchmark_config.num_iterations, len(dataset[split])),
            )
            bootstrapped_splits[split] = [
                dataset[split].select(bootstrap_indices[idx])
                for idx in range(benchmark_config.num_iterations)
            ]
        datasets = [
            DatasetDict(
                {
                    split: bootstrapped_splits[split][idx]
                    for split in dataset_config.splits
                }
            )
            for idx in range(benchmark_config.num_iterations)
        ]
    else:
        datasets = [dataset] * benchmark_config.num_iterations

    return datasets


def load_raw_data(dataset_config: "DatasetConfig", cache_dir: str) -> "DatasetDict":
    """Load the raw dataset.

    Args:
        dataset_config:
            The configuration for the dataset.
        cache_dir:
            The directory to cache the dataset.

    Returns:
        The dataset.
    """
    num_attempts = 5
    for _ in range(num_attempts):
        try:
            with no_terminal_output():
                dataset = load_dataset(
                    path=dataset_config.huggingface_id,
                    cache_dir=cache_dir,
                    token=unscramble("XbjeOLhwebEaSaDUMqqaPaPIhgOcyOfDpGnX_"),
                )
            break
        except (
            FileNotFoundError,
            ConnectionError,
            DatasetsError,
            requests.ConnectionError,
            requests.ReadTimeout,
        ) as e:
            log(
                f"Failed to load dataset {dataset_config.huggingface_id!r}, due to "
                f"the following error: {e}. Retrying...",
                level=logging.DEBUG,
            )
            time.sleep(1)
            continue
        except HfHubHTTPError:
            raise HuggingFaceHubDown()
    else:
        raise InvalidBenchmark(
            f"Failed to load dataset {dataset_config.huggingface_id!r} after "
            f"{num_attempts} attempts. Run with verbose mode to see the individual "
            "errors."
        )
    assert isinstance(dataset, DatasetDict)  # type: ignore[used-before-def]
    missing_keys = [key for key in dataset_config.splits if key not in dataset]
    if missing_keys:
        raise InvalidBenchmark(
            "The dataset is missing the following required splits: "
            f"{', '.join(missing_keys)}"
        )
    return DatasetDict({key: dataset[key] for key in dataset_config.splits})
