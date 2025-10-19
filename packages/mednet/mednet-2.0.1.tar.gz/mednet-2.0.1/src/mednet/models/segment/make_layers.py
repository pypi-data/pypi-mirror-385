# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import torch
import torch.nn
from torch.nn import Conv2d, ConvTranspose2d


def conv_with_kaiming_uniform(
    in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1
):
    """Convolution layer with kaiming uniform.

    Parameters
    ----------
    in_channels
        Number of input channels.
    out_channels
        Number of output channels.
    kernel_size
        The kernel size.
    stride
        The stride.
    padding
        The padding.
    dilation
        The dilation.

    Returns
    -------
        The convoluation layer.
    """
    conv = Conv2d(
        in_channels,
        out_channels,
        kernel_size=kernel_size,
        stride=stride,
        padding=padding,
        dilation=dilation,
        bias=True,
    )
    # Caffe2 implementation uses XavierFill, which in fact
    # corresponds to kaiming_uniform_ in PyTorch
    torch.nn.init.kaiming_uniform_(conv.weight, a=1)
    torch.nn.init.constant_(conv.bias, 0)
    return conv


def convtrans_with_kaiming_uniform(
    in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1
):
    """Implement convtrans layer with kaiming uniform.

    Parameters
    ----------
    in_channels
        Number of input channels.
    out_channels
        Number of output channels.
    kernel_size
        The kernel size.
    stride
        The stride.
    padding
        The padding.
    dilation
        The dilation.

    Returns
    -------
        The convtrans layer.
    """
    conv = ConvTranspose2d(
        in_channels,
        out_channels,
        kernel_size=kernel_size,
        stride=stride,
        padding=padding,
        dilation=dilation,
        bias=True,
    )
    # Caffe2 implementation uses XavierFill, which in fact
    # corresponds to kaiming_uniform_ in PyTorch
    torch.nn.init.kaiming_uniform_(conv.weight, a=1)
    torch.nn.init.constant_(conv.bias, 0)
    return conv


class UpsampleCropBlock(torch.nn.Module):
    """Combines Conv2d, ConvTransposed2d and Cropping. Simulates the caffe2
    crop layer in the forward function.

    Used for DRIU and HED.

    Parameters
    ----------
    in_channels
        Number of channels of intermediate layer.
    out_channels
        Number of output channels.
    up_kernel_size
        Kernel size for transposed convolution.
    up_stride
        Stride for transposed convolution.
    up_padding
        Padding for transposed convolution.
    pixelshuffle
        If True, uses PixelShuffleICNR upsampling.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        up_kernel_size: int,
        up_stride: int,
        up_padding: int,
        pixelshuffle: bool = False,
    ):
        super().__init__()
        # NOTE: Kaiming init, replace with torch.nn.Conv2d and
        # torch.nn.ConvTranspose2d to get original DRIU impl.
        self.conv = conv_with_kaiming_uniform(in_channels, out_channels, 3, 1, 1)
        if pixelshuffle:
            self.upconv = PixelShuffleICNR(out_channels, out_channels, scale=up_stride)
        else:
            self.upconv = convtrans_with_kaiming_uniform(
                out_channels,
                out_channels,
                up_kernel_size,
                up_stride,
                up_padding,
            )

    def forward(self, x, input_res):
        img_h = input_res[0]
        img_w = input_res[1]
        x = self.conv(x)
        x = self.upconv(x)
        # determine center crop
        # height
        up_h = x.shape[2]
        h_crop = up_h - img_h
        h_s = h_crop // 2
        h_e = up_h - (h_crop - h_s)
        # width
        up_w = x.shape[3]
        w_crop = up_w - img_w
        w_s = w_crop // 2
        w_e = up_w - (w_crop - w_s)
        # perform crop
        # needs explicit ranges for onnx export
        return x[:, :, h_s:h_e, w_s:w_e]  # crop to input size


def ifnone(a, b):
    """Return ``a`` if ``a`` is not None, otherwise ``b``.

    Parameters
    ----------
    a
        The first parameter.
    b
        The second parameter.

    Returns
    -------
        The parameter a if it is not None, else b.
    """
    return b if a is None else a


def icnr(x, scale=2, init=torch.nn.init.kaiming_normal_):
    """ICNR init of ``x``, with ``scale`` and ``init`` function.

    https://docs.fast.ai/layers.html#PixelShuffleICNR.

    Parameters
    ----------
    x
        Tensor.
    scale
        Scale of the upsample.
    init
        Function used to initialize.
    """

    ni, nf, h, w = x.shape
    ni2 = int(ni / (scale**2))
    k = init(torch.zeros([ni2, nf, h, w])).transpose(0, 1)
    k = k.contiguous().view(ni2, nf, -1)
    k = k.repeat(1, 1, scale**2)
    k = k.contiguous().view([nf, ni, h, w]).transpose(0, 1)
    x.data.copy_(k)


class PixelShuffleICNR(torch.nn.Module):
    """Upsample by ``scale`` from ``ni`` filters to ``nf`` (default
    ``ni``), using ``torch.nn.PixelShuffle``, ``icnr`` init, and
    ``weight_norm``.

    https://docs.fast.ai/layers.html#PixelShuffleICNR.

    Parameters
    ----------
    ni
        Number of initial filters.
    nf
        Number of final filters.
    scale
        Scale of the upsample.
    """

    def __init__(self, ni: int, nf: int | None = None, scale: int = 2):
        super().__init__()
        nf = ifnone(nf, ni)
        self.conv = conv_with_kaiming_uniform(ni, nf * (scale**2), 1)
        icnr(self.conv.weight)
        self.shuf = torch.nn.PixelShuffle(scale)
        # Blurring over (h*w) kernel, from
        # "Super-Resolution using Convolutional Neural Networks without Any
        # Checkerboard Artifacts", https://arxiv.org/abs/1806.02658
        self.pad = torch.nn.ReplicationPad2d((1, 0, 1, 0))
        self.blur = torch.nn.AvgPool2d(2, stride=1)
        self.relu = torch.nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.shuf(self.relu(self.conv(x)))
        return self.blur(self.pad(x))


class UnetBlock(torch.nn.Module):
    """Unet block implementation.

    Parameters
    ----------
    up_in_c
        Number of input channels.
    x_in_c
        Number of cat channels.
    pixel_shuffle
        If True, uses a PixelShuffleICNR layer for upsampling.
    middle_block
        If True, uses a middle block for VGG based U-Net.
    """

    def __init__(self, up_in_c, x_in_c, pixel_shuffle=False, middle_block=False):
        super().__init__()
        # middle block for VGG based U-Net
        if middle_block:
            up_out_c = up_in_c
        else:
            up_out_c = up_in_c // 2
        cat_channels = x_in_c + up_out_c
        inner_channels = cat_channels // 2

        if pixel_shuffle:
            self.upsample = PixelShuffleICNR(up_in_c, up_out_c)
        else:
            self.upsample = convtrans_with_kaiming_uniform(up_in_c, up_out_c, 2, 2)
        self.convtrans1 = convtrans_with_kaiming_uniform(
            cat_channels, inner_channels, 3, 1, 1
        )
        self.convtrans2 = convtrans_with_kaiming_uniform(
            inner_channels, inner_channels, 3, 1, 1
        )
        self.relu = torch.nn.ReLU(inplace=True)

    def forward(self, up_in, x_in):
        up_out = self.upsample(up_in)
        cat_x = torch.cat([up_out, x_in], dim=1)
        x = self.relu(self.convtrans1(cat_x))
        return self.relu(self.convtrans2(x))
