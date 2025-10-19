# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Holistically-Nested Edge Detection (HED) network architecture, from :cite:p:`xie_holistically-nested_2015`."""

import logging
import typing

import torch
import torch.nn
import torch.utils.data

from ...data.typing import TransformSequence
from ..losses import MultiLayerSoftJaccardAndBCELogitsLoss
from .backbones.vgg import vgg16_for_segmentation
from .make_layers import UpsampleCropBlock, conv_with_kaiming_uniform
from .model import Model

logger = logging.getLogger(__name__)


class ConcatFuseBlock(torch.nn.Module):
    """Take in five feature maps with one channel each, concatenates thems and applies a
    1x1 convolution with 1 output channel.
    """

    def __init__(self):
        super().__init__()
        self.conv = conv_with_kaiming_uniform(5, 1, 1, 1, 0)

    def forward(self, x1, x2, x3, x4, x5):
        x_cat = torch.cat([x1, x2, x3, x4, x5], dim=1)
        return self.conv(x_cat)


class HEDHead(torch.nn.Module):
    """HED head module.

    Parameters
    ----------
    in_channels_list : list
        Number of channels for each feature map that is returned from backbone.
    """

    def __init__(self, in_channels_list):
        super().__init__()
        (
            in_conv_1_2_16,
            in_upsample2,
            in_upsample_4,
            in_upsample_8,
            in_upsample_16,
        ) = in_channels_list

        self.conv1_2_16 = torch.nn.Conv2d(in_conv_1_2_16, 1, 3, 1, 1)
        # Upsample
        self.upsample2 = UpsampleCropBlock(in_upsample2, 1, 4, 2, 0)
        self.upsample4 = UpsampleCropBlock(in_upsample_4, 1, 8, 4, 0)
        self.upsample8 = UpsampleCropBlock(in_upsample_8, 1, 16, 8, 0)
        self.upsample16 = UpsampleCropBlock(in_upsample_16, 1, 32, 16, 0)
        # Concat and Fuse
        self.concatfuse = ConcatFuseBlock()

    def forward(self, x):
        hw = x[0]
        conv1_2_16 = self.conv1_2_16(x[1])
        upsample2 = self.upsample2(x[2], hw)
        upsample4 = self.upsample4(x[3], hw)
        upsample8 = self.upsample8(x[4], hw)
        upsample16 = self.upsample16(x[5], hw)
        concatfuse = self.concatfuse(
            conv1_2_16, upsample2, upsample4, upsample8, upsample16
        )

        return (upsample2, upsample4, upsample8, upsample16, concatfuse)


class HED(Model):
    """Holistically-Nested Edge Detection (HED) network architecture, from :cite:p:`xie_holistically-nested_2015`.

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
        loss_type: type[torch.nn.Module] = MultiLayerSoftJaccardAndBCELogitsLoss,
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
            name="hed",
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
            pretrained=pretrained, return_features=[3, 8, 14, 22, 29]
        )

        self.head = HEDHead([64, 128, 256, 512, 512])

    def forward(self, x):
        x = self.normalizer(x)
        x = self.backbone(x)
        return self.head(x)
