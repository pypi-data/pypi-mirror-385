# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""CHASE-DB1 dataset for vessel segmentation.

The CHASE_DB1 is a retinal vessel reference dataset acquired from multiethnic
school children. This database is a part of the Child Heart and Health Study in
England (CHASE), a cardiovascular health survey in 200 primary schools in
London, Birmingham, and Leicester. The ocular imaging was carried out in 46
schools and demonstrated associations between retinal vessel tortuosity and
early risk factors for cardiovascular disease in over 1000 British primary
school children of different ethnic origin. The retinal images of both of the
eyes of each child were recorded with a hand-held Nidek NM-200-D fundus camera.
The images were captured at 30 degrees FOV camera. The dataset of images are
characterized by having nonuniform back-ground illumination, poor contrast of
blood vessels as compared with the background and wider arteriolars that have a
bright strip running down the centre known as the central vessel reflex.

* Reference: :cite:p:`fraz_ensemble_2012`

Data specifications:

* Raw data input (on disk):

  * RGB images encoded in JPG format with resolution (HxW) = 960 x 999 pixels.
  * Vessel annotations are encoded as PNG images with the same resolution as
    input samples.
  * Masks for the eye fundus are provided by this package.
  * Total samples: 28

* Output sample:

    * Image: Load raw JPG images with :py:mod:`PIL`, with auto-conversion to RGB.
    * Vessel annotations: Load annotations with :py:mod:`PIL`, with
      auto-conversion to model ``1`` with no dithering.
    * Eye fundus mask: Load mask with :py:mod:`PIL`, with
      auto-conversion to model ``1`` with no dithering.

Split ``first-annotator`` contains 8 training samples and 20 tests samples
annotated by expert 1.  Split ``second-annotator`` contains the sample samples
as in ``first-annotator``, but annotated by expert 2.

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


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the Chase-db1 dataset."""

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
            A tuple containing path suffixes to the sample image, target, and mask
            to be loaded, within the dataset root folder.

        Returns
        -------
            The sample representation.
        """

        image = PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB")
        image = to_dtype(to_image(image), torch.float32, scale=True)

        target = self.target(sample)

        mask_path = (
            importlib.resources.files(__package__) / "masks" / DATABASE_SLUG / sample[2]
        )
        with importlib.resources.as_file(mask_path) as path:
            mask = PIL.Image.open(path).convert(mode="1", dither=None)
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

        target = PIL.Image.open(self.datadir / sample[1]).convert(mode="1", dither=None)
        return to_dtype(to_image(target), torch.float32, scale=True)


class DataModule(CachingDataModule):
    """CHASE-DB1 dataset for vessel segmentation.

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
