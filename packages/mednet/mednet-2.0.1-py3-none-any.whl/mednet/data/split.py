# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Concrete database-split loaders."""

import functools
import importlib.resources.abc
import json
import logging
import pathlib
import typing

import torch

from ..data.typing import DatabaseSplit, RawDataLoader

logger = logging.getLogger(__name__)


class JSONDatabaseSplit(DatabaseSplit):
    """Define a loader that understands a database split (train, test, etc) in
    JSON format.

    To create a new database split, you need to provide a JSON formatted
    dictionary in a file, with contents similar to the following:

    .. code-block:: json

       {
           "dataset1": [
               [
                   "sample1-data1",
                   "sample1-data2",
                   "sample1-data3",
               ],
               [
                   "sample2-data1",
                   "sample2-data2",
                   "sample2-data3",
               ]
           ],
           "dataset2": [
               [
                   "sample42-data1",
                   "sample42-data2",
                   "sample42-data3",
               ],
           ]
       }

    Your database split many contain any number of (raw) datasets (dictionary
    keys). For simplicity, we recommend to format all sample entries
    similarly so that raw-data-loading is simplified.  Use the function
    :py:func:`check_database_split_loading` to test raw data loading and fine
    tune the dataset split, or its loading.

    Objects of this class behave like a dictionary in which keys are dataset
    names in the split, and values represent samples data and meta-data. The
    actual JSON file descriptors are loaded on demand using
    a py:func:`functools.cached_property`.

    Parameters
    ----------
    path
        Absolute path to a JSON formatted file containing the database split to be
        recognized by this object.
    """

    def __init__(self, path: pathlib.Path | importlib.resources.abc.Traversable):
        self._path = path

    @functools.cached_property
    def _datasets(self) -> DatabaseSplit:
        """Return the DatabaseSplits.

        The first call to this (cached) property will trigger full .json file
        loading from disk.  Subsequent calls will be cached.

        Returns
        -------
        DatabaseSplit
            A dictionary mapping dataset names to lists of JSON objects.
        """

        if str(self._path).endswith(".bz2"):
            logger.debug(f"Loading database split from {str(self._path)}...")
            with __import__("bz2").open(self._path) as f:
                return json.load(f)
        else:
            with self._path.open() as f:
                return json.load(f)

    def __getitem__(self, key: str) -> typing.Sequence[typing.Any]:
        """Access dataset ``key`` from this split."""
        return self._datasets[key]

    def __iter__(self):
        """Iterate over the datasets."""
        return iter(self._datasets)

    def __len__(self) -> int:
        return len(self._datasets)


def check_database_split_loading(
    database_split: DatabaseSplit,
    loader: RawDataLoader,
    limit: int = 0,
) -> int:
    """For each dataset in the split, check if all data can be correctly loaded
    using the provided loader function.

    This function will return the number of errors when loading samples, and will
    log more detailed information to the logging stream.

    Parameters
    ----------
    database_split
        A mapping that contains the database split.  Each key represents the
        name of a dataset in the split.  Each value is a (potentially complex)
        object that represents a single sample.
    loader
        A loader object that knows how to handle full-samples.
    limit
        Maximum number of samples to check (in each split/dataset
        combination) in this dataset.  If set to zero, then check
        everything.

    Returns
    -------
    int
        Number of errors found.
    """

    logger.info(
        "Checking if all samples in all datasets of this split can be loaded...",
    )
    errors = 0
    for dataset, samples in database_split.items():
        samples = samples if not limit else samples[:limit]
        for pos, sample in enumerate(samples):
            try:
                data, _ = loader.sample(sample)
                assert isinstance(data, torch.Tensor)
            except Exception as e:
                logger.info(
                    f"Found error loading entry {pos} in dataset `{dataset}`: {e}",
                )
                errors += 1
    return errors


def make_split(module_name: str, basename: str) -> DatabaseSplit:
    """Return a database split at the provided module.

    This function searches for the database split named ``basename`` at the
    directory where module ``module_name`` is installed, and returns its
    instantiated version.

    Parameters
    ----------
    module_name
        Name of the module where to search for the JSON file.  It should be
        something like ``foo.bar`` for a module defined as
        ``foo/bar/__init__.py``, or ``foo/bar.py``.
    basename
        Name of the .json file containing the split to load.

    Returns
    -------
        An instance of a DatabaseSplit.
    """
    return JSONDatabaseSplit(importlib.resources.files(module_name) / basename)
