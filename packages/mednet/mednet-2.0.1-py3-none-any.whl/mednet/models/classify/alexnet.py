# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`AlexNet network architecture <alexnet-pytorch_>`_, from :cite:p:`krizhevsky_imagenet_2017`."""

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


class Alexnet(Model):
    """`AlexNet network architecture <alexnet-pytorch_>`_ model, from :cite:p:`krizhevsky_imagenet_2017`.

    Note: only usable with a normalized dataset

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
        num_classes: int = 1,
    ):
        super().__init__(
            name="alexnet",
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

        # Load pretrained model
        weights = None
        if self.pretrained:
            from ..normalizer import make_imagenet_normalizer

            Model.normalizer.fset(self, make_imagenet_normalizer())  # type: ignore[attr-defined]

            logger.info(f"Loading pretrained `{self.name}` model weights")
            weights = models.AlexNet_Weights.DEFAULT

        self.model = models.alexnet(weights=weights)

        self.model.classifier[4] = torch.nn.Linear(
            in_features=self.model.classifier[1].out_features, out_features=512
        )
        self.model.classifier[6] = torch.nn.Linear(
            in_features=self.model.classifier[4].out_features,
            out_features=self.num_classes,
        )

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        if self.num_classes != v:
            logger.info(
                f"Resetting `{self.name}` output classifier layer weights due "
                f"to a change in output size ({self.num_classes} -> {v})"
            )
            self.model.classifier[6] = torch.nn.Linear(
                in_features=self.model.classifier[4].out_features, out_features=v
            )
            self._num_classes = v

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        # reset number of output classes if need be
        self.num_classes = checkpoint["state_dict"]["model.classifier.bias"].shape[0]

        # perform routine checkpoint loading
        super().on_load_checkpoint(checkpoint)

    def forward(self, x):
        """Forward the input tensor through the network, producing a prediction.

        Parameters
        ----------
        x
            The tensor input to be forwarded.

        Returns
        -------
            The prediction, as a tensor.
        """
        x = self.normalizer(x)
        return self.model(x)
