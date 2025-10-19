# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`UNet network architecture <unet_>`_, from :cite:p:`navab_u-net_2015`."""

import logging
import typing

import torch.nn
import torch.utils.data

from ...data.typing import TransformSequence
from ..losses import SoftJaccardAndBCEWithLogitsLoss
from .backbones.vgg import vgg16_for_segmentation
from .make_layers import UnetBlock, conv_with_kaiming_uniform
from .model import Model

logger = logging.getLogger(__name__)


class UNetHead(torch.nn.Module):
    """UNet head module.

    Parameters
    ----------
    in_channels_list
        Number of channels for each feature map that is returned from backbone.
    pixel_shuffle
        If True, upsample using PixelShuffleICNR.
    """

    def __init__(self, in_channels_list: list[int], pixel_shuffle=False):
        super().__init__()
        # number of channels
        c_decode1, c_decode2, c_decode3, c_decode4, c_decode5 = in_channels_list

        # build layers
        self.decode4 = UnetBlock(c_decode5, c_decode4, pixel_shuffle, middle_block=True)
        self.decode3 = UnetBlock(c_decode4, c_decode3, pixel_shuffle)
        self.decode2 = UnetBlock(c_decode3, c_decode2, pixel_shuffle)
        self.decode1 = UnetBlock(c_decode2, c_decode1, pixel_shuffle)
        self.final = conv_with_kaiming_uniform(c_decode1, 1, 1)

    def forward(self, x: list[torch.Tensor]):
        """Forward pass.

        Parameters
        ----------
        x
            List of tensors as returned from the backbone network.
            First element: height and width of input image.
            Remaining elements: feature maps for each feature level.

        Returns
        -------
            OUtput of the forward pass.
        """
        # NOTE: x[0]: height and width of input image not needed in U-Net architecture
        decode4 = self.decode4(x[5], x[4])
        decode3 = self.decode3(decode4, x[3])
        decode2 = self.decode2(decode3, x[2])
        decode1 = self.decode1(decode2, x[1])
        return self.final(decode1)


class Unet(Model):
    """`UNet network architecture <unet_>`_, from :cite:p:`navab_u-net_2015`.

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
            name="unet",
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
            return_features=[3, 8, 14, 22, 29],
        )

        self.head = UNetHead([64, 128, 256, 512, 512], pixel_shuffle=False)

    def forward(self, x):
        x = self.normalizer(x)
        x = self.backbone(x)
        return self.head(x)
