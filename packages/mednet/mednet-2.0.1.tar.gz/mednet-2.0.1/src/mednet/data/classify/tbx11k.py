# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""TBX11k database for TB detection.

* Database reference: :cite:p:`liu_rethinking_2020`
* The original database contains samples of healthy, sick (no TB), active
  and latent TB cases.  There is a total of 11702 samples in the database.
  Healthy and sick individuals are kept in separate folders.  Latent and
  active TB cases are merged in the same directory.  One must check the
  radiological annotations to understand if samples contain either, or both
  (latent and active TB) signs.
* There is one case of patient (file ``imgs/tb/tb1199.png``), that is
  inside the ``tb`` folder, but contains no annotations.  This sample was
  **excluded** from our splits.
* There are 30 cases of patients that have both active and latent TB
  radiological signs, over the entire database.  Those samples were also
  **excluded** from our splits:

  - imgs/tb/tb0135.png
  - imgs/tb/tb0142.png
  - imgs/tb/tb0154.png
  - imgs/tb/tb0167.png
  - imgs/tb/tb0190.png
  - imgs/tb/tb0246.png
  - imgs/tb/tb0255.png
  - imgs/tb/tb0279.png
  - imgs/tb/tb0284.png
  - imgs/tb/tb0350.png
  - imgs/tb/tb0378.png
  - imgs/tb/tb0392.png
  - imgs/tb/tb0395.png
  - imgs/tb/tb0501.png
  - imgs/tb/tb0506.png
  - imgs/tb/tb0526.png
  - imgs/tb/tb0543.png
  - imgs/tb/tb0639.png
  - imgs/tb/tb0640.png
  - imgs/tb/tb0667.png
  - imgs/tb/tb0676.png
  - imgs/tb/tb0713.png
  - imgs/tb/tb0786.png
  - imgs/tb/tb0870.png
  - imgs/tb/tb0875.png
  - imgs/tb/tb0945.png
  - imgs/tb/tb0949.png
  - imgs/tb/tb0968.png
  - imgs/tb/tb1104.png
  - imgs/tb/tb1143.png

* Original train database samples:

  - Healthy: 3000
  - Sick (but no TB): 3000
  - Active TB only: 473
  - Latent TB only: 103
  - Both active and latent TB: 23
  - Unknown: 1
  - Total: 6600

* Original validation database samples:

  - Healthy: 800
  - Sick (but no TB): 800
  - Latent TB only: 36
  - Active TB only: 157
  - Both active and latent TB: 7
  - Total: 1800

* Original test database samples:

  - Unknown: 3302
  - Total: 3302

* Because the test set does not have annotations, we generated train,
  validation and test databases as such:

  - The original validation database becomes our test set.
  - The original train database is split into new train and validation
    splits (validation ratio = 0.203 w.r.t. original train database size).
    The selection of samples is stratified (see comments through our split
    code, which is shipped alongside this file.)

.. important:: **Raw data organization**

    The TBX11k_ base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least these two
    subdirectories:

    - ``imgs/`` (directory containing sub-directories and images in PNG format)
    - ``annotations/`` (directory containing labels in JSON and XML format)

Data specifications:

* Raw data input (on disk): PNG images 8 bits RGB, 512 x 512 pixels

* Output image:

  * Transforms:

    - Load raw PNG with :py:mod:`PIL`
    - Convert to torch tensor

  * Final specifications:

    - RGB, encoded as a 3-plane tensor using 32-bit floats, square
      (512x512 pixels)
    - Labels: 0 (healthy, latent tb or sick but no tb depending on the
      protocol), 1 (active tuberculosis), as a torch float tensor.
    - Bounding-boxes: indicating regions of the image that corroborate (active
      or latent TB diagnostics).

.. note:: **JSON Encoding**

   Details of the encoding of database splits in JSON format.

   For healthy/sick (no TB)/latent TB cases, each sample is represented by a
   filename, relative to the root of the installed database, followed by the
   number 0 (negative class).

   For active TB cases, each sample is represented by a filename, followed by
   the number 1, and then by 1 or more 5-tuples with radiological finding
   locations, as described above.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import copy
import importlib.resources.abc
import os
import pathlib
import typing

import PIL.Image
import torch
import torch.utils.data
import torchvision.transforms.v2
import torchvision.tv_tensors

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


DatabaseSample: typing.TypeAlias = (
    tuple[str, int] | tuple[str, int, tuple[tuple[int, int, int, int, int]]]
)
"""Type of objects in our JSON representation for this database.

For healthy/sick (no TB)/latent TB cases, each sample is represented by
a filename, relative to the root of the installed database, followed by
the number 0 (negative class).

For active TB cases, each sample is represented by a filename, followed
by the number 1, and then by 1 or more 5-tuples with radiological
finding locations, as described above.
"""


def custom_collate_fn(batch):  # numpydoc ignore=PR01
    """Collate samples that include bounding boxes.

    This allows us to have :py:class:`torchvision.tv_tensors.BoundingBoxes`
    that can contain zero to multiple boxes, which is not supported by the
    default collate function that uses :py:func:`torch.stack` for batching.

    Returns
    -------
        The given batch.
    """

    # A copy of the batch is needed, otherwise this function will permamnently
    # modify data in case it is cached.
    batch_ = copy.deepcopy(batch)

    if "bboxes" not in batch_[0].keys():
        return torch.utils.data.default_collate(batch_)

    # Remove the BoundingBoxes from the batch and apply the default collate
    # function
    bboxes = []
    bboxes_targets = []

    [bboxes.append(b.pop("bboxes")) for b in batch_]
    [bboxes_targets.append(b.pop("bbox_targets")) for b in batch_]

    out = torch.utils.data.default_collate(batch_)

    # Insert the BoundingBoxes and targets back as lists
    out["bboxes"] = bboxes
    out["bbox_targets"] = bboxes_targets

    return out


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the TBX11k database.

    Parameters
    ----------
    ignore_bboxes
        If True, sample() does not return bounding boxes.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self, ignore_bboxes: bool = False):
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
        )
        self.ignore_bboxes = ignore_bboxes

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the database root folder,
            where to find the image to be loaded, an integer, representing the
            sample target, and possible radiological findings represented by
            bounding boxes.

        Returns
        -------
            The sample representation.
        """

        image = PIL.Image.open(self.datadir / sample[0])
        image = torchvision.transforms.v2.functional.to_dtype(
            torchvision.transforms.v2.functional.to_image(image),
            torch.float32,
            scale=True,
        )
        image = torchvision.tv_tensors.Image(image)

        # use the code below to view generated images
        # from torchvision.transforms.v2.functional import to_pil_image
        # to_pil_image(tensor).show()
        # __import__("pdb").set_trace()

        if self.ignore_bboxes:
            return dict(image=image, target=self.target(sample), name=sample[0])

        bboxes, bbox_targets = self.bounding_boxes(
            sample, (image.shape[-2], image.shape[-1])
        )

        return dict(
            image=image,
            target=self.target(sample),
            name=sample[0],
            bboxes=bboxes,
            bbox_targets=bbox_targets,
        )

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

    def bounding_boxes(
        self, sample: typing.Any, canvas_size: tuple[int, int]
    ) -> tuple[torch.Tensor | None, torch.Tensor | None]:
        """Load image annotated bounding-boxes from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the database root folder,
            where to find the image to be loaded, an integer, representing the
            sample target, and possible radiological findings represented by
            bounding boxes.
        canvas_size
            Size of the full image.

        Returns
        -------
            Bounding box annotations, if any available with the sample, and
            their targets (1 for active TB, 0 for latent TB region).
        """

        if len(sample) > 2:
            bbox_data = [s[1:] for s in sample[2]]
            bboxes = torchvision.transforms.v2.functional.convert_bounding_box_format(
                torchvision.tv_tensors.BoundingBoxes(
                    data=bbox_data,
                    format=torchvision.tv_tensors.BoundingBoxFormat.XYWH,
                    canvas_size=canvas_size,
                ),
                new_format=torchvision.tv_tensors.BoundingBoxFormat.XYXY,
            )
            bbox_targets = [s[0] for s in sample[2]]
            return bboxes, torch.Tensor(bbox_targets).byte()

        return None, None


class DataModule(CachingDataModule):
    """TBX11k database for TB detection.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    ignore_bboxes
        If True, sample() does not return bounding boxes.
    """

    def __init__(
        self,
        split_path: pathlib.Path | importlib.resources.abc.Traversable,
        ignore_bboxes: bool = False,
    ):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(ignore_bboxes=ignore_bboxes),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            collate_fn=custom_collate_fn,
            num_classes=1,
        )
