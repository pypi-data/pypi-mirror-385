# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shenzhen DataModule for computer-aided diagnosis.

The standard digital image database for Tuberculosis was created by the
National Library of Medicine, Maryland, USA in collaboration with Shenzhen No.3
People’s Hospital, Guangdong Medical College, Shenzhen, China. The Chest X-rays
are from out-patient clinics, and were captured as part of the daily routine
using Philips DR Digital Diagnose systems.

* Database reference: :cite:p:`jaeger_two_2014`

.. important:: **Raw data organization**

    The Shenzhen_ base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at this subdirectory:

    - ``CXR_png/`` (directory containing the CXR images)

Data specifications:

* Raw data input (on disk):

  * PNG 8-bit RGB images issued from digital radiography machines (grayscale,
    but encoded as RGB images with "inverted" grayscale scale requiring special
    treatment).
  * Original resolution: variable width and height of 3000 x 3000 pixels or
    less
  * Samples: 662 images and associated labels

* Output image:

  * Transforms:

    * Load raw data with :py:mod:`PIL` with auto-conversion to grayscale
    * Remove (completely) black borders
    * Convert to torch tensor

  * Final specifications:

    * Grayscale, encoded as a single plane tensor, 32-bit floats,
      square with varying resolutions, depending on the input image
    * Labels: 0 (healthy), 1 (active tuberculosis)

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import PIL.Image
import torch
from torchvision import tv_tensors
from torchvision.transforms.v2.functional import to_dtype, to_image

from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..image_utils import remove_black_borders
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the Shenzhen dataset.

    Parameters
    ----------
    config_variable
        Key to search for in the configuration file for the root directory of
        this database.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    # config_variable: required so this loader can be used for the Indian
    # database as well.
    def __init__(self, config_variable: str = CONFIGURATION_KEY_DATADIR):
        self.datadir = pathlib.Path(
            load_rc().get(config_variable, os.path.realpath(os.curdir)),
        )

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The sample representation.
        """

        # N.B.: Image.convert("L") is required to normalize grayscale back to
        # normal (instead of inverted).
        image = PIL.Image.open(self.datadir / sample[0]).convert("L")
        image, _ = remove_black_borders(image)
        image = to_dtype(to_image(image), torch.float32, scale=True)
        image = tv_tensors.Image(image)

        # use the code below to view generated images
        # from torchvision.transforms.v2.functional import to_pil_image
        # to_pil_image(tensor).show()
        # __import__("pdb").set_trace()

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
    """Shenzhen DataModule for computer-aided diagnosis.

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
