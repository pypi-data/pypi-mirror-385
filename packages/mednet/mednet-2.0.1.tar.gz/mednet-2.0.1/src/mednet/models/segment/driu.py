# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""DRIU network architecture for vessel segmentation, from :cite:p:`maninis_deep_2016`."""

import logging
import typing

import torch
import torch.nn
import torch.utils.data

from ...data.typing import TransformSequence
from ..losses import SoftJaccardAndBCEWithLogitsLoss
from .backbones.vgg import vgg16_for_segmentation
from .make_layers import UpsampleCropBlock, conv_with_kaiming_uniform
from .model import Model

logger = logging.getLogger(__name__)


class ConcatFuseBlock(torch.nn.Module):
    """Takes in four feature maps with 16 channels each, concatenates them and
    applies a 1x1 convolution with 1 output channel.
    """

    def __init__(self):
        super().__init__()
        self.conv = conv_with_kaiming_uniform(4 * 16, 1, 1, 1, 0)

    def forward(self, x1, x2, x3, x4):
        x_cat = torch.cat([x1, x2, x3, x4], dim=1)
        return self.conv(x_cat)


class DRIUHead(torch.nn.Module):
    """DRIU head module.

    Based on paper by :cite:p:`maninis_deep_2016`.

    Parameters
    ----------
    in_channels_list
        Number of channels for each feature map that is returned from backbone.
    """

    def __init__(self, in_channels_list):
        super().__init__()
        (
            in_conv_1_2_16,
            in_upsample2,
            in_upsample_4,
            in_upsample_8,
        ) = in_channels_list

        self.conv1_2_16 = torch.nn.Conv2d(in_conv_1_2_16, 16, 3, 1, 1)
        # Upsample layers
        self.upsample2 = UpsampleCropBlock(in_upsample2, 16, 4, 2, 0)
        self.upsample4 = UpsampleCropBlock(in_upsample_4, 16, 8, 4, 0)
        self.upsample8 = UpsampleCropBlock(in_upsample_8, 16, 16, 8, 0)

        # Concat and Fuse
        self.concatfuse = ConcatFuseBlock()

    def forward(self, x):
        hw = x[0]
        conv1_2_16 = self.conv1_2_16(x[1])  # conv1_2_16
        upsample2 = self.upsample2(x[2], hw)  # side-multi2-up
        upsample4 = self.upsample4(x[3], hw)  # side-multi3-up
        upsample8 = self.upsample8(x[4], hw)  # side-multi4-up
        return self.concatfuse(conv1_2_16, upsample2, upsample4, upsample8)


class DRIU(Model):
    """DRIU network architecture for vessel segmentation, from :cite:p:`maninis_deep_2016`.

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
            name="driu",
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
            return_features=[3, 8, 14, 22],
        )

        self.head = DRIUHead([64, 128, 256, 512])

    def forward(self, x):
        x = self.normalizer(x)
        x = self.backbone(x)
        return self.head(x)
