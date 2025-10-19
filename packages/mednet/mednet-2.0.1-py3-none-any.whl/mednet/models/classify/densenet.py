# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`DenseNet-121 network architecture <densenet-pytorch_>`_, from :cite:p:`huang_densely_2017`."""

import logging
import typing

import torch
import torch.nn
import torch.optim.optimizer
import torch.utils.data
import torchvision.models as models

from ...data.typing import TransformSequence
from ..typing import Checkpoint
from .model import Model

logger = logging.getLogger(__name__)


class Densenet(Model):
    """`DenseNet-121 network architecture <densenet-pytorch_>`_, from :cite:p:`huang_densely_2017`.

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
    pretrained
        If set to True, loads pretrained model weights during initialization,
        else trains a new model.
    dropout
        Dropout rate after each dense layer.
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
        pretrained: bool = False,
        dropout: float = 0.1,
        num_classes: int = 1,
    ):
        super().__init__(
            name="densenet",
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

        self.pretrained = pretrained
        self.dropout = dropout

        # Load pretrained model
        weights = None
        if self.pretrained:
            from ..normalizer import make_imagenet_normalizer

            Model.normalizer.fset(self, make_imagenet_normalizer())  # type: ignore[attr-defined]

            logger.info(f"Loading pretrained `{self.name}` model weights")
            weights = models.DenseNet121_Weights.DEFAULT

        self.model = models.densenet121(weights=weights, drop_rate=self.dropout)

        # output layer
        self.model.classifier = torch.nn.Linear(
            self.model.classifier.in_features, self.num_classes
        )

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        if self.num_classes != v:
            logger.info(
                f"Resetting `{self.name}` output classifier layer weights due "
                f"to a change in output size ({self.num_classes} -> {v})"
            )
            self.model.classifier = torch.nn.Linear(
                self.model.classifier.in_features, v
            )
            self._num_classes = v

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        # support previous version of densenet (model_ft -> model)
        if any([k.startswith("model_ft") for k in checkpoint["state_dict"].keys()]):
            # convert all "model_ft" entries to "model"
            checkpoint["state_dict"] = {
                k.replace("model_ft", "model"): v
                for k, v in checkpoint["state_dict"].items()
            }

        # reset number of output classes if need be
        self.num_classes = checkpoint["state_dict"]["model.classifier.bias"].shape[0]

        # perform routine checkpoint loading
        super().on_load_checkpoint(checkpoint)

    def forward(self, x):
        x = self.normalizer(x)
        return self.model(x)
