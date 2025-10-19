# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""NIH CXR14 (relabeled) DataModule for computer-aided diagnosis.

This dataset was extracted from the clinical PACS database at the National
Institutes of Health Clinical Center (USA) and represents 60% of all their
radiographs. It contains labels for 14 common radiological signs in this order:
cardiomegaly, emphysema, effusion, hernia, infiltration, mass, nodule,
atelectasis, pneumothorax, pleural thickening, pneumonia, fibrosis, edema and
consolidation. Training and validation data come from the **relabeled** version
created in the :cite:p:`rajpurkar_deep_2018` study. Test data uses the available annotations with
:cite:p:`wang_chestx-ray8_2017`.

* Database references:

  * Original data: :cite:p:`wang_chestx-ray8_2017` (contains 112'120 chest X-ray images) and
    up to 14 associated radiological findings.
  * Labels and split references: We use train and validation splits published
    at :cite:p:`rajpurkar_deep_2018`, that are `available here` <nih-cxr14-relabeled_>`_.
    These are **different compared to the file lists provided with the original
    :cite:p:`wang_chestx-ray8_2017` study** (train/val set: 86'523 samples; test set: 25'595
    samples; +2 missing samples which are not listed, making up 112'120
    samples). The splits at :cite:p:`rajpurkar_deep_2018`, which we copied in this library,
    contain 104'987 samples which were relabeled making up a training and a
    validation set containing 98'637 and 6'350 samples respectively.  Note the
    relabeling work provided by :cite:p:`rajpurkar_deep_2018` does not provide **test** set
    annotations (only training and validation).  Our test set then consists of
    all CXR8_ samples that were not relabled, and for which we reused the
    `original CXR8 annotations <cxr8_>`_ (7'133 samples).

.. important:: **Raw data organization**

    The CXR8_ base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least the directory
    "images/" with all the images of the database.

    The labels from :cite:p:`rajpurkar_deep_2018` (`available here <nih-cxr14-relabeled_>`_)
    are already incorporated in this library and do **not** need to be
    re-downloaded.

    The flag ``idiap_folder_structure`` makes the loader search for files
    named, e.g. ``images/00030621_006.png``, as
    ``images/00030/00030621_006.png``.

* Raw data input (on disk):

  * PNG RGB 8-bit depth images
  * Original resolution: 1024 x 1024 pixels
  * Non-exclusive labels organized in a (compact) string list encoded
    as such:

    0. ``car``: cardiomegaly
    1. ``emp``: emphysema
    2. ``eff``: effusion
    3. ``her``: hernia
    4. ``inf``: infiltration
    5. ``mas``: mass
    6. ``nod``: nodule
    7. ``ate``: atelectasis
    8. ``pnt``: pneumothorax
    9. ``plt``: pleural thickening
    10. ``pne``: pneumonia
    11. ``fib``: fibrosis
    12. ``ede``: edema
    13. ``con``: consolidation

  * Patient age (integer)
  * Patient gender ("M" or "F")
  * Total samples available: 112'120

* Output image:

  * Transforms:

    * Load raw PNG with :py:mod:`PIL`, with auto-conversion to grayscale
    * Convert to torch tensor

  * Final specifications:

    * RGB, encoded as a 3-plane tensor, 32-bit floats, square
      (1024x1024 px)

      This decoder loads this description and converts it to a binary
      multi-label representation.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import numpy
import PIL.Image
import torch
from torchvision import tv_tensors
from torchvision.transforms.v2.functional import to_dtype, to_image

from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir.cxr8"
"""Key to search for in the configuration file for the root directory of this
database."""

CONFIGURATION_KEY_IDIAP_FILESTRUCTURE = "cxr8.idiap_folder_structure"
"""Key to search for in the configuration file indicating if the loader should
use standard or idiap-based file organisation structure.

It causes the internal loader to search for files in a slightly
different folder structure, that was adapted to Idiap's requirements
(number of files per folder to be less than 10k).
"""

RADIOLOGICAL_FINDINGS = [
    "car",  # cardiomegaly
    "emp",  # emphysema
    "eff",  # effusion
    "her",  # hernia
    "inf",  # infiltration
    "mas",  # mass
    "nod",  # nodule
    "ate",  # atelectasis
    "pnt",  # pneumothorax
    "plt",  # pleural thickening
    "pne",  # pneumonia
    "fib",  # fibrosis
    "ede",  # edema
    "con",  # consolidation
]
"""List of radiological findings (abbreviations) supported on this database."""

_RADIOLOGICAL_FINDINGS_MAPPINGS = {
    k: numpy.eye(1, len(RADIOLOGICAL_FINDINGS), i, dtype=float)[0]
    for i, k in enumerate(RADIOLOGICAL_FINDINGS)
}
"""Auto-calculated radiological findings mapping between strings and position vectors."""


def binarize_findings(lst: list[str]) -> torch.Tensor:
    """Binarize the input list of radiological findings.

    The output list contains zeros and ones, respecting the findings order in
    :py:data:`RADIOLOGICAL_FINDINGS`.

    Parameters
    ----------
    lst
        A list of radiological findings that will be converted.

    Returns
    -------
        A list containing a binarized version of the input list.
    """
    return torch.tensor(
        numpy.array(
            [numpy.zeros(len(RADIOLOGICAL_FINDINGS), dtype=float)]
            + [_RADIOLOGICAL_FINDINGS_MAPPINGS[k] for k in lst]
        ).sum(0),
    ).float()


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the NIH CXR-14 dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    idiap_file_organisation: bool
    """If should use the Idiap's filesystem organisation when looking up data.

    This variable will be ``True``, if the user has set the configuration
    parameter ``nih_cxr14.idiap_file_organisation`` in the global configuration
    file.  It will cause internal loader to search for files in a slightly
    different folder structure, that was adapted to Idiap's requirements
    (number of files per folder to be less than 10k).
    """

    def __init__(self):
        rc = load_rc()
        self.datadir = pathlib.Path(
            rc.get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir)),
        )
        self.idiap_file_organisation = rc.get(
            CONFIGURATION_KEY_IDIAP_FILESTRUCTURE,
            False,
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

        file_path = pathlib.Path(sample[0])  # default
        if self.idiap_file_organisation:
            # for folder lookup efficiency, data is split into subfolders
            # each original file is on the subfolder `f[:5]/f`, where f
            # is the original file basename
            file_path = pathlib.Path(
                file_path.parent / file_path.name[:5] / file_path.name
            )

        # N.B.: some NIH CXR-14 images are encoded as color PNGs with an alpha
        # channel.  Most, are grayscale PNGs
        image = PIL.Image.open(self.datadir / file_path).convert(mode="L")
        image = to_dtype(to_image(image), torch.float32, scale=True)
        image = tv_tensors.Image(image)

        # use the code below to view generated images
        # from torchvision.transforms.v2.functional import to_pil_image
        # to_pil_image(tensor).show()
        # __import__("pdb").set_trace()

        return dict(image=image, target=self.target(sample), name=sample[0])

    def target(self, sample: typing.Any) -> torch.Tensor:
        """Load only sample target from its raw representation.

        The raw representation contains zero to many (unique) instances of
        radiological findings listed at :py:data:`RADIOLOGICAL_FINDINGS`.  This
        list is binarized (into 14 binary ositions) before it is returned.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing the
            sample target.

        Returns
        -------
            The labels corresponding to all radiological signs present in the
            specified sample, encapsulated as a 1D torch float tensor.
        """

        return binarize_findings(sample[1])


class DataModule(CachingDataModule):
    """NIH CXR14 (relabeled) DataModule for computer-aided diagnosis.

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
            num_classes=14,
        )
