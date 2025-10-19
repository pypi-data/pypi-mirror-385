# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""VISCERAL dataset for 3D organ classification (only lungs and bladders).

* Database reference: :cite:p:`jimenez-del-toro_cloud-based_2016`

Data specifications:

* Raw data input (on disk):

  * NIfTI volumes
  * resolution: 16x16x16 pixels - Loaded samples are not full scans but
    16x16x16 volumes of organs.

* Output image:

  * Transforms:

    * Load raw NIfTI with `torchio <https://torchio.readthedocs.io/>`_
    * Clamp and Rescale intensity
    * Convert to torch tensor

  * Final specifications

    * 32-bit floats, cubes 16x16x16 pixels
    * targets: 0 (bladder), 1 (lung)

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import torch
import torchio as tio
from torchvision import tv_tensors

from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the VISCERAL database."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self) -> None:
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
        )

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single volume sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the database root folder,
            where to find the volume to be loaded and an integer, representing
            the sample target.

        Returns
        -------
            The sample representation.
        """
        clamp = tio.Clamp(out_min=-1000, out_max=2000)
        rescale = tio.RescaleIntensity(percentiles=(0.5, 99.5))
        preprocess = tio.Compose([clamp, rescale])
        image = tio.ScalarImage(self.datadir / sample[0])
        image = preprocess(image)
        image = tv_tensors.Image(image.data)
        return dict(image=image, target=self.target(sample), name=sample[0])

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
            1D torch float tensor.
        """

        return torch.FloatTensor([sample[1]])


class DataModule(CachingDataModule):
    """VISCERAL DataModule for 3D organ binary classification.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    """

    def __init__(self, split_path: pathlib.Path | importlib.resources.abc.Traversable):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            num_classes=1,
        )
