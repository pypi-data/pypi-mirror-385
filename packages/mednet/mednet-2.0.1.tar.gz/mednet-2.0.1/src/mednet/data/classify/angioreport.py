# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""AngioReport dataset for automatic report generation on angiography images.

The AngioReport Dataset is the first publicly available angiographic dataset,
comprising images of both fluorescein angiography and indocyanine green angiography (ICGA),
all labeled by retinal specialists.  Collected at the Department of
Ophthalmology, Rajavithi Hospital, Bangkok, Thailand, the final dataset consists of  55,361
images from 1,691 patients (3,179 eyes). Among the 3,179 eyes, 81.8% were examined in both
FA and ICGA modes, 10.3% underwent FA only, and the remaining 7.9% had ICGA only. Since
angiographic imaging methods are non-standardized and vary based on the specialist and patient,
the number of images per eye in this dataset ranges from a few to several hundred. The only
labeled images are those present in the original training split (33,559 images from 1,921 eyes).

The dataset covers 24 medical conditions and provides detailed descriptions of the type, location,
shape, size, and pattern of abnormal fluorescence. Specifically:
- Impression [multilabel]
- HyperF_Type [multiclass]
- HyperF_Area(DA) [multiclass]
- HyperF_Fovea [binary]
- HyperF_ExtraFovea	[multilabel]
- HyperF_Y [multilabel]
- HypoF_Type [multiclass]
- HypoF_Area(DA) [multiclass]
- HypoF_Fovea [binary]
- HypoF_ExtraFovea [multilabel]
- HypoF_Y [multilabel]
- CNV [binary]
- Vascular abnormality (DR)	[multilabel]
- Pattern [multilabel]

In the current setup, we include only those samples that were examined in both FA and ICGA modes,
identifiable by their aspect ratio, specifically, images whose width is twice their height, as these
represent concatenated pairs of both modalities. For each eye, we select only the last frame image,
which is typically the most informative for diagnosis. This selection results in a total of 1,887
samples/eyes.

Data specifications:

* Raw data input (on disk):

  * JPEG grayscale images encoded as 8-bit sRGB, with varying resolution
    (most images being 384 x 364 pixels or 256 x 256 pixels, after being
    cropped to obtain images of one of the two modalities).
  * Total samples: 30,768 (FA/ICGA images) (Only last frame 1887)

* Output image:

  * Transforms:

    * Load raw JPEG with :py:mod:`PIL`, with auto-conversion to grayscale
    * Crop images to obtain the specified modality (FA or ICGA)
    * Convert to torch tensor

* Final specifications

  * Grayscale, encoded as a single plane tensor, 32-bit floats, with varying
    resolution depending on input.
  * Labels: they depend on the task selected.

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

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""

IMPRESSION_TYPE_ICGA = [
    "unremarkable changes",
    "macular neovascularization",
    "central serous chorioretinopathy",
    "uveitis",
    "polypoidal choroidal vasculopathy",
    "pachychoroid pigment epitheliopathy",
    "choroidal mass",
    "Other",
]
"""List of impression type detectable from icga."""

_IMPRESSION_TYPE_ICGA_MAPPINGS = {
    k: numpy.eye(1, len(IMPRESSION_TYPE_ICGA), i, dtype=float)[0]
    for i, k in enumerate(IMPRESSION_TYPE_ICGA)
}
"""Auto-calculated impression mapping between strings and position vectors."""


def binarize_findings(lst: list[str]) -> torch.Tensor:
    """Binarize the input list of radiological findings.

    The output list contains zeros and ones, respecting the findings order in
    :py:data:`IMPRESSION_TYPE_ICGA`.

    Parameters
    ----------
    lst
        A list of impression type that will be converted.

    Returns
    -------
        A list containing a binarized version of the input list.
    """
    return torch.tensor(
        numpy.array(
            [numpy.zeros(len(IMPRESSION_TYPE_ICGA), dtype=float)]
            + [_IMPRESSION_TYPE_ICGA_MAPPINGS[k] for k in lst]
        ).sum(0),
    ).float()


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the AngioReport dataset.

    Parameters
    ----------
    problem_type
        Specifies the problem type for the current split. Can be ``binary`` or ``multiclass``.
        This parameter controls how the target labels are processed and retrieved from the
        dataset.
    modality
        Specifies the modality to be used. Can be ``FA`` (Fluorescein Angiography) or ``ICGA`` (Indocyanine Green Angiography).
        Default is ``FA``. Depending on the modality a different crop operation is performed on the input image.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(
        self,
        problem_type: typing.Literal["binary", "multiclass", "multilabel"],
        modality: typing.Literal["FA", "ICGA"] = "FA",
    ):
        # Make sure that your mednet.toml file has an entry in datadir.angioreport with the right path to the dataset
        # problem_type is already set up to add "multilabel". Not supported at the moment
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
        )
        # This attribute changes the way the target is retrieved
        self.problem_type = problem_type
        # This attribute changes the way the image is cropped
        self.modality = modality

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            Expects a tuple containing the path suffix, within the dataset root
            folder, where to find the image to be loaded, and an integer,
            representing the sample target.

        Returns
        -------
            The sample representation.
        """

        image = PIL.Image.open(self.datadir / sample[0]).convert("L")
        # crop the image to get only FA/ICGA image
        width, height = image.size
        box = (
            (0, 0, width - width / 2, height - 50)
            if self.modality == "FA"
            else (width - width / 2, 0, width, height - 50)
        )
        image = image.crop(box)

        image = to_dtype(to_image(image), torch.float32, scale=True)
        image = tv_tensors.Image(image)

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
            1D torch float or 0D long tensor (depending on the problem_type).
        """
        if self.problem_type == "binary":
            return torch.FloatTensor([sample[1]])
        if self.problem_type == "multilabel":
            return binarize_findings(sample[1])
        return torch.LongTensor([sample[1]]).squeeze()


class DataModule(CachingDataModule):
    """AngioReport dataset.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    num_classes
        Number of output classes for the task at hand.
    problem_type
        Specifies the problem type for the current split. Can be ``binary``, ``multilabel`` or ``multiclass``.
        This parameter controls how the target labels are processed and retrieved from the
        dataset.
    modality
        Specifies the modality to be used. Can be ``FA`` (Fluorescein Angiography) or ``ICGA`` (Indocyanine Green Angiography).
        Default is ``FA``. Depending on the modality a different crop operation is performed on the input image.
    """

    def __init__(
        self,
        split_path: pathlib.Path | importlib.resources.abc.Traversable,
        num_classes: int,
        problem_type: typing.Literal["binary", "multiclass", "multilabel"],
        modality: typing.Literal["FA", "ICGA"] = "FA",
    ):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(problem_type, modality),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            num_classes=num_classes,
        )
