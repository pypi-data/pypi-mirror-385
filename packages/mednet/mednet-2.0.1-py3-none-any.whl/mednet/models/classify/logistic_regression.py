# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`Logistic regression model <logistic-regression_>`_ for multi-class classification."""

import logging
import typing

import torch
import torch.nn

from ..typing import Checkpoint
from .model import Model

logger = logging.getLogger(__name__)


class LogisticRegression(Model):
    """`Logistic regression model <logistic-regression_>`_ for multi-class classification.

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
    num_classes
        Number of outputs (classes) for this model.
    input_size
        The number of inputs this classifer shall process.
    """

    def __init__(
        self,
        loss_type: type[torch.nn.Module] = torch.nn.BCEWithLogitsLoss,
        loss_arguments: dict[str, typing.Any] | None = None,
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] | None = {"lr": 1e-2},
        num_classes: int = 1,
        input_size: int = 14,
    ):
        super().__init__(
            name="logistic-regression",
            loss_type=loss_type,
            loss_arguments=loss_arguments,
            optimizer_type=optimizer_type,
            optimizer_arguments=optimizer_arguments,
            scheduler_type=None,
            scheduler_arguments=None,
            model_transforms=None,
            augmentation_transforms=None,
            num_classes=num_classes,
        )

        self.input_size = input_size
        self.num_classes = num_classes

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        self.linear = torch.nn.Linear(self.input_size, v)
        self._num_classes = v

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        num_classes = checkpoint["state_dict"]["linear.bias"].shape[0]

        if num_classes != self.num_classes:
            logger.debug(
                f"Resetting number-of-output-classes at `{self.name}` model from "
                f"{self.num_classes} to {num_classes} while loading checkpoint."
            )
        self.num_classes = num_classes

        super().on_load_checkpoint(checkpoint)

    def forward(self, x):
        return self.linear(self.normalizer(x))
