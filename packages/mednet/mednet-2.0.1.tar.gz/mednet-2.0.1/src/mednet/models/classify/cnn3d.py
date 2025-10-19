# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple 3D convolutional neural network architecture for classification."""

import logging
import typing

import torch
import torch.nn as nn
import torch.nn.functional as F  # noqa: N812
import torch.optim.optimizer
import torch.utils.data

from ...data.typing import TransformSequence
from ..typing import Checkpoint
from .model import Model

logger = logging.getLogger(__name__)


class Conv3DNet(Model):
    """Simple 3D convolutional neural network architecture for classification.

    This network has a linear output.  You should use losses with ``WithLogit``
    instead of cross-entropy versions when training.

    Parameters
    ----------
    loss_type
        The loss to be used for training and evaluation.

        .. warning::

           The loss should be set to always return batch averages (as opposed
           to the batch sum), as our logging system expects it so.
    loss_arguments
        Arguments to the loss.
    optimizer_type
        The type of optimizer to use for training.
    optimizer_arguments
        Arguments to the optimizer after ``params``.
    scheduler_type
        The type of scheduler to use for training.
    scheduler_arguments
        Arguments to the scheduler after ``params``.
    model_transforms
        An optional sequence of torch modules containing transforms to be
        applied on the input **before** it is fed into the network.
    augmentation_transforms
        An optional sequence of torch modules containing transforms to be
        applied on the input **before** it is fed into the network.
    num_classes
        Number of outputs (classes) for this model.
    """

    def __init__(
        self,
        loss_type: type[torch.nn.Module] = torch.nn.BCEWithLogitsLoss,
        loss_arguments: dict[str, typing.Any] = {},
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] = {},
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] = {},
        model_transforms: TransformSequence = [],
        augmentation_transforms: TransformSequence = [],
        num_classes: int = 1,
    ):
        super().__init__(
            name="cnn3d",
            loss_type=loss_type,
            loss_arguments=loss_arguments,
            optimizer_type=optimizer_type,
            optimizer_arguments=optimizer_arguments,
            scheduler_type=scheduler_type,
            scheduler_arguments=scheduler_arguments,
            model_transforms=model_transforms,
            augmentation_transforms=augmentation_transforms,
            num_classes=num_classes,
        )

        # First convolution block
        self.conv3d_1_1 = nn.Conv3d(
            in_channels=1, out_channels=4, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_1_2 = nn.Conv3d(
            in_channels=4, out_channels=16, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_1_3 = nn.Conv3d(
            in_channels=1, out_channels=16, kernel_size=1, stride=1
        )
        self.batch_norm_1_1 = nn.BatchNorm3d(4)
        self.batch_norm_1_2 = nn.BatchNorm3d(16)
        self.batch_norm_1_3 = nn.BatchNorm3d(16)

        # Second convolution block
        self.conv3d_2_1 = nn.Conv3d(
            in_channels=16, out_channels=24, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_2_2 = nn.Conv3d(
            in_channels=24, out_channels=32, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_2_3 = nn.Conv3d(
            in_channels=16, out_channels=32, kernel_size=1, stride=1
        )
        self.batch_norm_2_1 = nn.BatchNorm3d(24)
        self.batch_norm_2_2 = nn.BatchNorm3d(32)
        self.batch_norm_2_3 = nn.BatchNorm3d(32)

        # Third convolution block
        self.conv3d_3_1 = nn.Conv3d(
            in_channels=32, out_channels=40, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_3_2 = nn.Conv3d(
            in_channels=40, out_channels=48, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_3_3 = nn.Conv3d(
            in_channels=32, out_channels=48, kernel_size=1, stride=1
        )
        self.batch_norm_3_1 = nn.BatchNorm3d(40)
        self.batch_norm_3_2 = nn.BatchNorm3d(48)
        self.batch_norm_3_3 = nn.BatchNorm3d(48)

        # Fourth convolution block
        self.conv3d_4_1 = nn.Conv3d(
            in_channels=48, out_channels=56, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_4_2 = nn.Conv3d(
            in_channels=56, out_channels=64, kernel_size=3, stride=1, padding=1
        )
        self.conv3d_4_3 = nn.Conv3d(
            in_channels=48, out_channels=64, kernel_size=1, stride=1
        )
        self.batch_norm_4_1 = nn.BatchNorm3d(56)
        self.batch_norm_4_2 = nn.BatchNorm3d(64)
        self.batch_norm_4_3 = nn.BatchNorm3d(64)

        self.pool = nn.MaxPool3d(2)
        self.global_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.dropout = nn.Dropout(0.3)
        self.fc1 = nn.Linear(64, 32)
        self.num_classes = num_classes

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        self.fc2 = nn.Linear(32, v)
        self._num_classes = v

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        num_classes = checkpoint["state_dict"]["fc2.bias"].shape[0]

        if num_classes != self.num_classes:
            logger.debug(
                f"Resetting number-of-output-classes at `{self.name}` model from "
                f"{self.num_classes} to {num_classes} while loading checkpoint."
            )
        self.num_classes = num_classes

        super().on_load_checkpoint(checkpoint)

    def forward(self, x):
        x = self.normalizer(x)  # type: ignore

        # First convolution block
        _x = x
        x = F.relu(self.batch_norm_1_1(self.conv3d_1_1(x)))
        x = F.relu(self.batch_norm_1_2(self.conv3d_1_2(x)))
        x = (x + F.relu(self.batch_norm_1_3(self.conv3d_1_3(_x)))) / 2
        x = self.pool(x)

        # Second convolution block

        _x = x
        x = F.relu(self.batch_norm_2_1(self.conv3d_2_1(x)))
        x = F.relu(self.batch_norm_2_2(self.conv3d_2_2(x)))
        x = (x + F.relu(self.batch_norm_2_3(self.conv3d_2_3(_x)))) / 2
        x = self.pool(x)

        # Third convolution block

        _x = x
        x = F.relu(self.batch_norm_3_1(self.conv3d_3_1(x)))
        x = F.relu(self.batch_norm_3_2(self.conv3d_3_2(x)))
        x = (x + F.relu(self.batch_norm_3_3(self.conv3d_3_3(_x)))) / 2
        x = self.pool(x)

        # Fourth convolution block

        _x = x
        x = F.relu(self.batch_norm_4_1(self.conv3d_4_1(x)))
        x = F.relu(self.batch_norm_4_2(self.conv3d_4_2(x)))
        x = (x + F.relu(self.batch_norm_4_3(self.conv3d_4_3(_x)))) / 2

        x = self.global_pool(x)
        x = x.view(x.size(0), x.size(1))

        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)

        # x = F.log_softmax(x, dim=1) # 0 is batch size
