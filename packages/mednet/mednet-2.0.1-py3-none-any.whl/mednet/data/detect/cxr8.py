# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""ChestX-ray8: Hospital-scale Chest X-ray Database transformed for lung detection.

Check :py:mod:`.segment.cxr8` for details.  This module only uses the segmentation
utilities to provide an "object detection" interface.

* Output sample:

    * Image: As per :py:mod:`.segment.cxr8`.
    * Bounding-box: A single bounding-box accounting for the observed lung region.

This module contains the base declaration of common data modules and raw-data loaders
for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import pathlib
import typing

import torch
from torchvision import tv_tensors
from torchvision.ops import masks_to_boxes

from ..datamodule import CachingDataModule
from ..segment.cxr8 import CONFIGURATION_KEY_DATADIR, DATABASE_SLUG
from ..segment.cxr8 import RawDataLoader as BaseDataLoader
from ..split import JSONDatabaseSplit
from ..typing import Sample


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the cxr8 dataset."""

    def __init__(self):
        super().__init__()

        # keep this on this module for correct database script support!
        assert CONFIGURATION_KEY_DATADIR

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder, where to
            find the image to be loaded, and an integer, representing the sample label.

        Returns
        -------
            The sample representation.
        """

        retval = super().sample(sample)

        target = tv_tensors.BoundingBoxes(
            data=self.target(sample),
            format=tv_tensors.BoundingBoxFormat.XYXY,
            canvas_size=retval["image"].shape[-2:],
        )

        return dict(
            image=retval["image"],
            target=target,
            labels=torch.FloatTensor([1]),  # background is 0
            mask=retval["mask"],
            name=sample[0],
        )

    def target(self, sample: typing.Any) -> torch.Tensor:
        """Load only sample target from its raw representation.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder, where to
            find the image to be loaded, and an integer, representing the sample target.

        Returns
        -------
            The label corresponding to the specified sample, encapsulated as a torch
            float tensor.
        """

        # converts target into bounding box
        return masks_to_boxes(super().target(sample))


class DataModule(CachingDataModule):
    """ChestX-ray8: Hospital-scale Chest X-ray Database for lung detection.

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
            task="detection",
            num_classes=1,
        )
