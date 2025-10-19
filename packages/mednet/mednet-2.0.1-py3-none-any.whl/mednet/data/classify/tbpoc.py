# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""TB-POC dataset for computer-aided diagnosis.

This databases contain only the tuberculosis final diagnosis (0 or 1) and come
from HIV infected patients.

* Database reference: :cite:p:`griesel_optimizing_2018`

.. important:: **Raw data organization**

    The TB-POC base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least the directory
    ``TBPOC_CXR`` with all JPEG images.

Data specifications:

* Raw data input (on disk):

  * JPEG 8-bit Grayscale images
  * Original resolution (height x width or width x height): 2048 x 2500 pixels
    or 2500 x 2048 pixels
  * Total samples: 407

* Output image:

  * Transforms:

    * Load raw grayscale jpeg with :py:mod:`PIL`
    * Remove black borders
    * Convert to torch tensor
    * Torch center cropping to get square image

  * Final specifications:

    * Grayscale, encoded as a single plane tensor, 32-bit floats,
      square with varying resolutions (2048 x 2048 being the maximum),
      but also depending on black borders' sizes on the input image.
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
    """A specialized raw-data-loader for the Shenzen dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
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

        # images from TBPOC are encoded as grayscale JPEGs, no need to
        # call convert("L") here.
        image = PIL.Image.open(self.datadir / sample[0])
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
    """TB-POC dataset for computer-aided diagnosis.

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
