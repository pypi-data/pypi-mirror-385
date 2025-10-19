# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""RIM-ONE r3 (training set) for cup segmentation.

The dataset contains 159 stereo eye fundus images with a resolution of 2144 x
1424. The right part of the stereo image is disregarded. Two sets of
ground-truths for optic disc and optic cup are available. The first set is
commonly used for training and testing. The second set acts as a “human”
baseline.  A third set, composed of annotation averages may also be used for
training and evaluation purposes.

* Reference: :cite:p:`fumero_interactive_2015`
* Original resolution (height x width): 1424 x 1072
* Split reference: :cite:p:`maninis_deep_2016`
* Protocols ``optic-disc-exp1``, ``optic-cup-exp1``, ``optic-disc-exp2``,
  ``optic-cup-exp2``, ``optic-disc-avg`` and ``optic-cup-avg``
* Training: 99
* Test: 60

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources
import importlib.resources.abc
import os
import pathlib
import typing

import PIL.Image
import torch
from torchvision import tv_tensors
from torchvision.transforms.v2.functional import to_dtype, to_image

from ...models.transforms import crop_image_to_mask
from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name to refer to this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""

_CROP_COORDINATES = (0, 0, 1072, 1424)
"""Crop RIM-ONE r3 image to avoid (right-side) stereo pair.

* Coordinates are (torchvision): top = 0, left = 0, height = 1424, width = 1072
* Coordinates are (PIL): left = 0, upper = 0, right = 1072, lower = 1424
"""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the rimoner3 dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing the
            sample label.

        Returns
        -------
            The sample representation.
        """

        image = (
            PIL.Image.open(self.datadir / sample[0])
            .convert(mode="RGB")
            .crop(_CROP_COORDINATES)
        )
        image = to_dtype(to_image(image), torch.float32, scale=True)

        target = self.target(sample)

        mask_path = (
            importlib.resources.files(__package__) / "masks" / DATABASE_SLUG / sample[2]
        )
        with importlib.resources.as_file(mask_path) as path:
            mask = (
                PIL.Image.open(path)
                .convert(mode="1", dither=None)
                .crop(_CROP_COORDINATES)
            )
            mask = to_dtype(to_image(mask), torch.float32, scale=True)

        image = tv_tensors.Image(crop_image_to_mask(image, mask))
        target = tv_tensors.Mask(crop_image_to_mask(target, mask))
        mask = tv_tensors.Mask(mask)

        return dict(image=image, target=target, mask=mask, name=sample[0])

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

        target = (
            PIL.Image.open(self.datadir / sample[1])
            .convert(mode="1", dither=None)
            .crop(_CROP_COORDINATES)
        )
        return to_dtype(to_image(target), torch.float32, scale=True)


class DataModule(CachingDataModule):
    """RIM-ONE r3 (training set) for cup segmentation.

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
            task="segmentation",
            num_classes=1,
        )
