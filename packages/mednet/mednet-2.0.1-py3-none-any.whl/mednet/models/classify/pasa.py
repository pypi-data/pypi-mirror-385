# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple CNN network model from :cite:p:`pasa_efficient_2019`."""

import logging
import typing

import torch
import torch.nn
import torch.nn.functional as F  # noqa: N812
import torch.optim.optimizer
import torch.utils.data

from ...data.typing import TransformSequence
from ..typing import Checkpoint
from .model import Model

logger = logging.getLogger(__name__)


class Pasa(Model):
    """Simple CNN network model from :cite:p:`pasa_efficient_2019`.

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
        loss_arguments: dict[str, typing.Any] | None = None,
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] | None = None,
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] | None = None,
        model_transforms: TransformSequence | None = None,
        augmentation_transforms: TransformSequence | None = None,
        num_classes: int = 1,
    ):
        super().__init__(
            name="pasa",
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
        self.fc1 = torch.nn.Conv2d(1, 4, (3, 3), (2, 2), (1, 1))
        self.fc2 = torch.nn.Conv2d(4, 16, (3, 3), (2, 2), (1, 1))
        self.fc3 = torch.nn.Conv2d(1, 16, (1, 1), (4, 4))

        self.batchNorm2d_4 = torch.nn.BatchNorm2d(4)
        self.batchNorm2d_16 = torch.nn.BatchNorm2d(16)
        self.batchNorm2d_16_2 = torch.nn.BatchNorm2d(16)

        # Second convolution block
        self.fc4 = torch.nn.Conv2d(16, 24, (3, 3), (1, 1), (1, 1))
        self.fc5 = torch.nn.Conv2d(24, 32, (3, 3), (1, 1), (1, 1))
        self.fc6 = torch.nn.Conv2d(
            16,
            32,
            (1, 1),
            (1, 1),
        )  # Original stride (2, 2)

        self.batchNorm2d_24 = torch.nn.BatchNorm2d(24)
        self.batchNorm2d_32 = torch.nn.BatchNorm2d(32)
        self.batchNorm2d_32_2 = torch.nn.BatchNorm2d(32)

        # Third convolution block
        self.fc7 = torch.nn.Conv2d(32, 40, (3, 3), (1, 1), (1, 1))
        self.fc8 = torch.nn.Conv2d(40, 48, (3, 3), (1, 1), (1, 1))
        self.fc9 = torch.nn.Conv2d(
            32,
            48,
            (1, 1),
            (1, 1),
        )  # Original stride (2, 2)

        self.batchNorm2d_40 = torch.nn.BatchNorm2d(40)
        self.batchNorm2d_48 = torch.nn.BatchNorm2d(48)
        self.batchNorm2d_48_2 = torch.nn.BatchNorm2d(48)

        # Fourth convolution block
        self.fc10 = torch.nn.Conv2d(48, 56, (3, 3), (1, 1), (1, 1))
        self.fc11 = torch.nn.Conv2d(56, 64, (3, 3), (1, 1), (1, 1))
        self.fc12 = torch.nn.Conv2d(
            48,
            64,
            (1, 1),
            (1, 1),
        )  # Original stride (2, 2)

        self.batchNorm2d_56 = torch.nn.BatchNorm2d(56)
        self.batchNorm2d_64 = torch.nn.BatchNorm2d(64)
        self.batchNorm2d_64_2 = torch.nn.BatchNorm2d(64)

        # Fifth convolution block
        self.fc13 = torch.nn.Conv2d(64, 72, (3, 3), (1, 1), (1, 1))
        self.fc14 = torch.nn.Conv2d(72, 80, (3, 3), (1, 1), (1, 1))
        self.fc15 = torch.nn.Conv2d(
            64,
            80,
            (1, 1),
            (1, 1),
        )  # Original stride (2, 2)

        self.batchNorm2d_72 = torch.nn.BatchNorm2d(72)
        self.batchNorm2d_80 = torch.nn.BatchNorm2d(80)
        self.batchNorm2d_80_2 = torch.nn.BatchNorm2d(80)

        self.pool2d = torch.nn.MaxPool2d(
            (3, 3),
            (2, 2),
        )  # Pool after conv. block

        self.dense = torch.nn.Linear(80, self.num_classes)  # Fully connected layer

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        if self.num_classes != v:
            logger.info(
                f"Resetting `{self.name}` output classifier layer weights due "
                f"to change in output size ({self.num_classes} -> {v})"
            )
            self.dense = torch.nn.Linear(80, v)  # Fully connected layer
            self._num_classes = v

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        # reset number of output classes if need be
        self.num_classes = checkpoint["state_dict"]["dense.bias"].shape[0]

        # perform routine checkpoint loading
        super().on_load_checkpoint(checkpoint)

    def forward(self, x):
        x = self.normalizer(x)  # type: ignore

        # First convolution block
        _x = x
        x = F.relu(self.batchNorm2d_4(self.fc1(x)))  # 1st convolution
        x = F.relu(self.batchNorm2d_16(self.fc2(x)))  # 2nd convolution
        x = (x + F.relu(self.batchNorm2d_16_2(self.fc3(_x)))) / 2  # Parallel
        x = self.pool2d(x)  # Pooling

        # Second convolution block
        _x = x
        x = F.relu(self.batchNorm2d_24(self.fc4(x)))  # 1st convolution
        x = F.relu(self.batchNorm2d_32(self.fc5(x)))  # 2nd convolution
        x = (x + F.relu(self.batchNorm2d_32_2(self.fc6(_x)))) / 2  # Parallel
        x = self.pool2d(x)  # Pooling

        # Third convolution block
        _x = x
        x = F.relu(self.batchNorm2d_40(self.fc7(x)))  # 1st convolution
        x = F.relu(self.batchNorm2d_48(self.fc8(x)))  # 2nd convolution
        x = (x + F.relu(self.batchNorm2d_48_2(self.fc9(_x)))) / 2  # Parallel
        x = self.pool2d(x)  # Pooling

        # Fourth convolution block
        _x = x
        x = F.relu(self.batchNorm2d_56(self.fc10(x)))  # 1st convolution
        x = F.relu(self.batchNorm2d_64(self.fc11(x)))  # 2nd convolution
        x = (x + F.relu(self.batchNorm2d_64_2(self.fc12(_x)))) / 2  # Parallel
        x = self.pool2d(x)  # Pooling

        # Fifth convolution block
        _x = x
        x = F.relu(self.batchNorm2d_72(self.fc13(x)))  # 1st convolution
        x = F.relu(self.batchNorm2d_80(self.fc14(x)))  # 2nd convolution
        x = (x + F.relu(self.batchNorm2d_80_2(self.fc15(_x)))) / 2  # Parallel
        # no pooling

        # Global average pooling
        x = torch.mean(x.view(x.size(0), x.size(1), -1), dim=2)

        # Dense layer
        return self.dense(x)

        # x = F.log_softmax(x, dim=1) # 0 is batch size
