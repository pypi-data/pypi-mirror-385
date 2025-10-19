# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defines most common types used in code."""

import abc
import collections.abc
import typing

import torch
import torch.utils.data

Sample: typing.TypeAlias = typing.Mapping[str, typing.Any]
"""Definition of a sample.

A dictionary containing an arbitrary number of keys and values.  Some of the
keys are reserved, others ignored within the framework, and can be re-used to
hold sample metadata required for further analysis.

Reserved keys:

* ``input``: This is typically a 1, 2 or 3D torch float tensor containing the
  input data to be analysed.
* ``target``: This is typically a torch float tensor containing the target the
  network must try to achieve. In the case of classification, it can be a 1D
  tensor containing a single entry (binary classification) or multiple entries
  (multi-class classification).  In the case of semantic segmentation, this
  entry typically contains a float representation of the target mask the
  network must decode from the ``input`` data.
* ``mask``: A torch float tensor containing a mask over which the input (and
  the output) may be ignored.  Typically used in semantic segmentation tasks.
* ``name``: A name for the sample.  Typically set to the name of the file or
  file-stem holding the ``input`` data.
"""


class RawDataLoader(abc.ABC):
    """A loader object can load samples from storage."""

    @abc.abstractmethod
    def sample(self, sample: typing.Any) -> Sample:
        """Load whole samples from media.

        Parameters
        ----------
        sample
            Information about the sample to load. Implementation dependent.

        Returns
        -------
            The instantiated sample, which is a dictionary where keys name the
            sample's data and metadata.
        """
        pass

    @abc.abstractmethod
    def target(self, sample: typing.Any) -> torch.Tensor:
        """Load only sample target from its raw representation.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The label corresponding to the specified sample, encapsulated as a
            torch float tensor.
        """
        pass


Transform: typing.TypeAlias = typing.Callable[[torch.Tensor], torch.Tensor]
"""A callable that transforms tensors into (other) tensors.

Typically used in data-processing pipelines inside pytorch.
"""

TransformSequence: typing.TypeAlias = typing.Sequence[Transform]
"""A sequence of transforms."""

DatabaseSplit: typing.TypeAlias = collections.abc.Mapping[
    str,
    typing.Sequence[typing.Any],
]
"""The definition of a database split.

A database split maps dataset (subset) names to sequences of objects that,
through a :py:class:`RawDataLoader`, eventually becomes a :py:data:`.Sample` in
the processing pipeline.
"""

ConcatDatabaseSplit: typing.TypeAlias = collections.abc.Mapping[
    str,
    typing.Sequence[tuple[typing.Sequence[typing.Any], RawDataLoader]],
]
"""The definition of a complex database split composed of several other splits.

A database split maps dataset (subset) names to sequences of objects that,
through a :py:class:`.RawDataLoader`, eventually becomes a :py:data:`.Sample` in
the processing pipeline. Objects of this subtype allow the construction of
complex splits composed of cannibalized parts of other splits.  Each split may
be assigned a different :py:class:`.RawDataLoader`.
"""


class Dataset(torch.utils.data.Dataset[Sample], typing.Iterable, typing.Sized):
    """Our own definition of a pytorch Dataset.

    We iterate over Sample objects in this case.  Our datasets always
    provide a dunder len method.
    """

    def targets(self) -> list[torch.Tensor]:
        """Return the integer targets for all samples in the dataset."""
        raise NotImplementedError("You must implement the `targets()` method")


DataLoader: typing.TypeAlias = torch.utils.data.DataLoader[Sample]
"""Our own augmentation definition of a pytorch DataLoader.

We iterate over Sample objects in this case.
"""
