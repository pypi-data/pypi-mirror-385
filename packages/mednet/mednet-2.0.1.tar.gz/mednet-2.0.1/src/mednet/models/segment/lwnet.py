# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`Little W-Net (LWNET) network architecture <lwnet_>`_, from :cite:p:`galdran_state---art_2022`.

It is based on two simple U-Nets with 3 layers concatenated to each other.  The first
U-Net produces a segmentation map that is used by the second to better guide
segmentation.
"""

import logging
import typing

import torch
import torch.nn

from ...data.typing import TransformSequence
from ...utils.string import rewrap
from ..losses import MultiLayerBCELogitsLossWeightedPerBatch
from .model import Model

logger = logging.getLogger(__name__)


def _conv1x1(in_planes, out_planes, stride=1):
    return torch.nn.Conv2d(
        in_planes, out_planes, kernel_size=1, stride=stride, bias=False
    )


class ConvBlock(torch.nn.Module):
    """Convolution block.

    Parameters
    ----------
    input_channels
        Number of input channels.
    output_channels
        Number of output channels.
    kernel_size
        Kernel Size.
    add_conv2d
        If True, adds a Conv2d layer.
    add_max_pool2d
        If True, adds a MaxPool2d layer.
    """

    def __init__(
        self,
        input_channels,
        output_channels,
        kernel_size=3,
        add_conv2d=False,
        add_max_pool2d=True,
    ):
        super().__init__()
        if add_conv2d is True:
            self.conv2d_layer = torch.nn.Sequential(
                _conv1x1(input_channels, output_channels),
                torch.nn.BatchNorm2d(output_channels),
            )
        else:
            self.conv2d_layer = None
        pad = (kernel_size - 1) // 2

        block = []
        self.pool = None
        if add_max_pool2d:
            self.pool = torch.nn.MaxPool2d(kernel_size=2)

        block.append(
            torch.nn.Conv2d(
                input_channels, output_channels, kernel_size=kernel_size, padding=pad
            )
        )
        block.append(torch.nn.ReLU())
        block.append(torch.nn.BatchNorm2d(output_channels))

        block.append(
            torch.nn.Conv2d(
                output_channels, output_channels, kernel_size=kernel_size, padding=pad
            )
        )
        block.append(torch.nn.ReLU())
        block.append(torch.nn.BatchNorm2d(output_channels))

        self.block = torch.nn.Sequential(*block)

    def forward(self, x: torch.Tensor):
        if self.pool is not None:
            x = self.pool(x)
        out = self.block(x)
        if self.conv2d_layer is not None:
            return out + self.conv2d_layer(x)
        return out


class UpsampleBlock(torch.nn.Module):
    """Upsample block implementation.

    Parameters
    ----------
    input_channels
        Number of input channels.
    output_channels
        Number of output channels.
    upsampling_mode
        Upsampling mode.
    """

    def __init__(
        self,
        input_channels: int,
        output_channels: int,
        upsampling_mode: typing.Literal["transp_conv", "up_conv"],
    ):
        super().__init__()
        block = []

        match upsampling_mode:
            case "transp_conv":
                block.append(
                    torch.nn.ConvTranspose2d(
                        input_channels, output_channels, kernel_size=2, stride=2
                    )
                )
            case "up_conv":
                block.append(
                    torch.nn.Upsample(
                        mode="bilinear", scale_factor=2, align_corners=False
                    )
                )
                block.append(
                    torch.nn.Conv2d(input_channels, output_channels, kernel_size=1)
                )
            case _:
                raise NotImplementedError(
                    "Upsampling mode `{upsampling_mode}` is not supported"
                )

        self.block = torch.nn.Sequential(*block)

    def forward(self, x):
        return self.block(x)


class ConvBridgeBlock(torch.nn.Module):
    """ConvBridgeBlock implementation.

    Parameters
    ----------
    channels
        Number of channels.
    kernel_size
        Kernel Size.
    """

    def __init__(self, channels: int, kernel_size: int):
        super().__init__()
        pad = (kernel_size - 1) // 2
        block = []

        block.append(
            torch.nn.Conv2d(channels, channels, kernel_size=kernel_size, padding=pad)
        )
        block.append(torch.nn.ReLU())
        block.append(torch.nn.BatchNorm2d(channels))

        self.block = torch.nn.Sequential(*block)

    def forward(self, x):
        return self.block(x)


class UpConvBlock(torch.nn.Module):
    """UpConvBlock implementation.

    Parameters
    ----------
    input_channels
        Number of input channels.
    output_channels
        Number of output channels.
    kernel_size
        Kernel Size.
    upsampling_mode
        Upsampling mode.
    add_conv_bridge
        If True, adds a ConvBridgeBlock layer.
    add_conv2d
        If True, adds a Conv2d layer.
    """

    def __init__(
        self,
        input_channels: int,
        output_channels: int,
        kernel_size: int = 3,
        upsampling_mode: typing.Literal["transp_conv", "up_conv"] = "up_conv",
        add_conv_bridge: bool = False,
        add_conv2d: bool = False,
    ):
        super().__init__()
        self.add_conv_bridge = add_conv_bridge

        self.up_layer = UpsampleBlock(
            input_channels=input_channels,
            output_channels=output_channels,
            upsampling_mode=upsampling_mode,
        )
        self.conv_layer = ConvBlock(
            2 * output_channels,
            output_channels,
            kernel_size=kernel_size,
            add_conv2d=add_conv2d,
            add_max_pool2d=False,
        )
        if self.add_conv_bridge:
            self.add_conv_bridge_layer = ConvBridgeBlock(
                channels=output_channels, kernel_size=kernel_size
            )

    def forward(self, x, skip):
        up = self.up_layer(x)
        if self.add_conv_bridge:
            out = torch.cat([up, self.add_conv_bridge_layer(skip)], dim=1)
        else:
            out = torch.cat([up, skip], dim=1)
        return self.conv_layer(out)


class LittleUNet(torch.nn.Module):
    """Base little U-Net (LUNET) network architecture, from :cite:p:`galdran_state---art_2022`.

    Parameters
    ----------
    input_channels
        Number of input channels.
    layers
        Number of layers of the model.
    num_classes
        Number of outputs (classes) for this model.
    kernel_size
        Kernel Size.
    upsampling_mode
        Upsampling mode.
    add_conv_bridge
        If True, adds a ConvBridgeBlock layer.
    add_conv2d
        If True, adds a Conv2d layer.
    """

    def __init__(
        self,
        input_channels,
        layers,
        num_classes: int = 1,
        kernel_size: int = 3,
        upsampling_mode: typing.Literal["transp_conv", "up_conv"] = "transp_conv",
        add_conv_bridge=True,
        add_conv2d=True,
    ):
        super().__init__()

        self.name = "lunet"
        self._num_classes = num_classes
        self.layers = layers
        self.first = ConvBlock(
            input_channels=input_channels,
            output_channels=self.layers[0],
            kernel_size=kernel_size,
            add_conv2d=add_conv2d,
            add_max_pool2d=False,
        )

        self.down_path = torch.nn.ModuleList()
        for i in range(len(self.layers) - 1):
            block = ConvBlock(
                input_channels=self.layers[i],
                output_channels=self.layers[i + 1],
                kernel_size=kernel_size,
                add_conv2d=add_conv2d,
                add_max_pool2d=True,
            )
            self.down_path.append(block)

        self.up_path = torch.nn.ModuleList()
        reversed_layers = list(reversed(self.layers))
        for i in range(len(self.layers) - 1):
            block = UpConvBlock(
                input_channels=reversed_layers[i],
                output_channels=reversed_layers[i + 1],
                kernel_size=kernel_size,
                upsampling_mode=upsampling_mode,
                add_conv_bridge=add_conv_bridge,
                add_conv2d=add_conv2d,
            )
            self.up_path.append(block)

        # init, shamelessly lifted from torchvision/models/resnet.py
        for m in self.modules():
            if isinstance(m, torch.nn.Conv2d):
                torch.nn.init.kaiming_normal_(
                    m.weight, mode="fan_out", nonlinearity="relu"
                )
            elif isinstance(m, torch.nn.BatchNorm2d | torch.nn.GroupNorm):
                torch.nn.init.constant_(m.weight, 1)
                torch.nn.init.constant_(m.bias, 0)

        self.final = torch.nn.Conv2d(self.layers[0], self._num_classes, kernel_size=1)

    def forward(self, x):
        x = self.first(x)
        down_activations = []
        for i, down in enumerate(self.down_path):
            down_activations.append(x)
            x = down(x)
        down_activations.reverse()
        for i, up in enumerate(self.up_path):
            x = up(x, down_activations[i])
        return self.final(x)

    @property
    def num_classes(self) -> int:
        """Number of outputs (classes) for this model.

        Returns
        -------
        int
            The number of outputs supported by this model.
        """
        return self._num_classes

    @num_classes.setter
    def num_classes(self, v: int) -> None:
        if self._num_classes != v:
            logger.info(
                rewrap(
                    f"""Resetting `{self.name}` unet1 conv2d layer weights and the
                    **whole** unet2 due to a change in output size ({self.num_classes}
                    -> {v})"""
                )
            )
            self.final = torch.nn.Conv2d(self.layers[0], v, kernel_size=1)
            self._num_classes = v


class LittleWNet(Model):
    """`Little W-Net (LWNET) network architecture <lwnet_>`_, from :cite:p:`galdran_state---art_2022`.

    Concatenates two :py:class:`Little U-Net <LittleUNet>` models.

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
        loss_type: type[torch.nn.Module] = MultiLayerBCELogitsLossWeightedPerBatch,
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
            name="lwnet",
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

        self.unet1 = LittleUNet(
            input_channels=3,
            num_classes=self.num_classes,
            layers=(8, 16, 32),
            add_conv_bridge=True,
            add_conv2d=True,
        )
        self.unet2 = LittleUNet(
            input_channels=3 + self.num_classes,
            num_classes=self.num_classes,
            layers=(8, 16, 32),
            add_conv_bridge=True,
            add_conv2d=True,
        )

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        if self.num_classes != v:
            logger.info(
                rewrap(
                    f"""Resetting `{self.name}` unet1 conv2d layer weights and the
                    **whole** unet2 due to a change in output size ({self.num_classes}
                    -> {v})"""
                )
            )
            self.unet1.num_classes = v
            self.unet2 = LittleUNet(
                input_channels=3 + v,
                num_classes=v,
                layers=(8, 16, 32),
                add_conv_bridge=True,
                add_conv2d=True,
            )
            self._num_classes = v

    def forward(self, x):
        x = self.normalizer(x)
        x1 = self.unet1(x)
        x2 = self.unet2(torch.cat([x, x1], dim=1))
        return x1, x2

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        del batch_idx, dataloader_idx  # satisfies linter
        # prediction only returns the result of the last lunet
        return torch.sigmoid(self(batch["image"])[1])
