# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""DRIU network architecture for optic-disc segmentation, from :cite:p:`maninis_deep_2016`."""

import logging
import typing

import torch
import torch.nn
import torch.utils.data

from ...data.typing import TransformSequence
from ..losses import SoftJaccardAndBCEWithLogitsLoss
from .backbones.vgg import vgg16_for_segmentation
from .driu import ConcatFuseBlock
from .make_layers import UpsampleCropBlock
from .model import Model

logger = logging.getLogger(__name__)


class DRIUODHead(torch.nn.Module):
    """DRIU for optic disc segmentation head module.

    Parameters
    ----------
    in_channels_list : list
        Number of channels for each feature map that is returned from backbone.
    """

    def __init__(self, in_channels_list):
        super().__init__()
        (
            in_upsample2,
            in_upsample_4,
            in_upsample_8,
            in_upsample_16,
        ) = in_channels_list

        self.upsample2 = UpsampleCropBlock(in_upsample2, 16, 4, 2, 0)
        # Upsample layers
        self.upsample4 = UpsampleCropBlock(in_upsample_4, 16, 8, 4, 0)
        self.upsample8 = UpsampleCropBlock(in_upsample_8, 16, 16, 8, 0)
        self.upsample16 = UpsampleCropBlock(in_upsample_16, 16, 32, 16, 0)

        # Concat and Fuse
        self.concatfuse = ConcatFuseBlock()

    def forward(self, x):
        hw = x[0]
        upsample2 = self.upsample2(x[1], hw)  # side-multi2-up
        upsample4 = self.upsample4(x[2], hw)  # side-multi3-up
        upsample8 = self.upsample8(x[3], hw)  # side-multi4-up
        upsample16 = self.upsample16(x[4], hw)  # side-multi5-up
        return self.concatfuse(upsample2, upsample4, upsample8, upsample16)


class DRIUOD(Model):
    """DRIU network architecture for optic-disc segmentation, from :cite:p:`maninis_deep_2016`.

    Parameters
    ----------
    loss_type
        The loss to be used for training and evaluation.

        .. warning::

           The loss should be set to always return batch averages (as opposed to the
           batch sum), as our logging system expects it so.
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
        An optional sequence of torch modules containing transforms to be applied on the
        input **before** it is fed into the network.
    augmentation_transforms
        An optional sequence of torch modules containing transforms to be applied on the
        input **before** it is fed into the network.
    pretrained
        If True, will use VGG16 pretrained weights.
    """

    def __init__(
        self,
        loss_type: type[torch.nn.Module] = SoftJaccardAndBCEWithLogitsLoss,
        loss_arguments: dict[str, typing.Any] | None = None,
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] | None = None,
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] | None = None,
        model_transforms: TransformSequence | None = None,
        augmentation_transforms: TransformSequence | None = None,
        pretrained: bool = False,
    ):
        super().__init__(
            name="driu-od",
            loss_type=loss_type,
            loss_arguments=loss_arguments,
            optimizer_type=optimizer_type,
            optimizer_arguments=optimizer_arguments,
            scheduler_type=scheduler_type,
            scheduler_arguments=scheduler_arguments,
            model_transforms=model_transforms,
            augmentation_transforms=augmentation_transforms,
            num_classes=1,  # fixed at current implementation
        )

        if pretrained:
            from ..normalizer import make_imagenet_normalizer

            Model.normalizer.fset(self, make_imagenet_normalizer())  # type: ignore[attr-defined]

        self.backbone = vgg16_for_segmentation(
            pretrained=pretrained,
            return_features=[8, 14, 22, 29],
        )

        self.head = DRIUODHead([128, 256, 512, 512])

    def forward(self, x):
        x = self.normalizer(x)
        x = self.backbone(x)
        return self.head(x)
