# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Mobile2 UNet network architecture, from :cite:p:`laibacher_m2u-net_2018`."""

import logging
import typing

import torch
import torch.nn
import torch.utils.data
from torchvision.models.mobilenetv2 import InvertedResidual

from ...data.typing import TransformSequence
from ..losses import SoftJaccardAndBCEWithLogitsLoss
from .backbones.mobilenetv2 import mobilenet_v2_for_segmentation
from .model import Model

logger = logging.getLogger(__name__)


class DecoderBlock(torch.nn.Module):
    """Decoder block: upsample and concatenate with features maps from the
    encoder part.

    Parameters
    ----------
    up_in_c
        Number of input channels.
    x_in_c
        Number of cat channels.
    upsamplemode
        Mode to use for upsampling.
    expand_ratio
        The expand ratio.
    """

    def __init__(self, up_in_c, x_in_c, upsamplemode="bilinear", expand_ratio=0.15):
        super().__init__()
        self.upsample = torch.nn.Upsample(
            scale_factor=2, mode=upsamplemode, align_corners=False
        )  # H, W -> 2H, 2W
        self.ir1 = InvertedResidual(
            up_in_c + x_in_c,
            (x_in_c + up_in_c) // 2,
            stride=1,
            expand_ratio=expand_ratio,
        )

    def forward(self, up_in, x_in):
        up_out = self.upsample(up_in)
        cat_x = torch.cat([up_out, x_in], dim=1)
        return self.ir1(cat_x)


class LastDecoderBlock(torch.nn.Module):
    """Last decoder block.

    Parameters
    ----------
    x_in_c
        Number of cat channels.
    upsamplemode
        Mode to use for upsampling.
    expand_ratio
        The expand ratio.
    """

    def __init__(self, x_in_c, upsamplemode="bilinear", expand_ratio=0.15):
        super().__init__()
        self.upsample = torch.nn.Upsample(
            scale_factor=2, mode=upsamplemode, align_corners=False
        )  # H, W -> 2H, 2W
        self.ir1 = InvertedResidual(x_in_c, 1, stride=1, expand_ratio=expand_ratio)

    def forward(self, up_in, x_in):
        up_out = self.upsample(up_in)
        cat_x = torch.cat([up_out, x_in], dim=1)
        return self.ir1(cat_x)


class M2UNetHead(torch.nn.Module):
    """M2U-Net head module.

    Parameters
    ----------
    in_channels_list
        Number of channels for each feature map that is returned from backbone.
    upsamplemode
        Mode to use for upsampling.
    expand_ratio
        The expand ratio.
    """

    def __init__(
        self, in_channels_list=None, upsamplemode="bilinear", expand_ratio=0.15
    ):
        super().__init__()

        # Decoder
        self.decode4 = DecoderBlock(96, 32, upsamplemode, expand_ratio)
        self.decode3 = DecoderBlock(64, 24, upsamplemode, expand_ratio)
        self.decode2 = DecoderBlock(44, 16, upsamplemode, expand_ratio)
        self.decode1 = LastDecoderBlock(33, upsamplemode, expand_ratio)

        # initilaize weights
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, torch.nn.Conv2d):
                torch.nn.init.kaiming_uniform_(m.weight, a=1)
                if m.bias is not None:
                    torch.nn.init.constant_(m.bias, 0)
            elif isinstance(m, torch.nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x):
        decode4 = self.decode4(x[5], x[4])  # 96, 32
        decode3 = self.decode3(decode4, x[3])  # 64, 24
        decode2 = self.decode2(decode3, x[2])  # 44, 16
        return self.decode1(decode2, x[1])  # 30, 3


class M2Unet(Model):
    """Mobile2 UNet network architecture, from :cite:p:`laibacher_m2u-net_2018`.

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
            name="m2unet",
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

        self.backbone = mobilenet_v2_for_segmentation(
            pretrained=pretrained,
            return_features=[1, 3, 6, 13],
        )

        self.head = M2UNetHead(in_channels_list=[16, 24, 32, 96])

    def forward(self, x):
        x = self.normalizer(x)
        x = self.backbone(x)
        return self.head(x)
