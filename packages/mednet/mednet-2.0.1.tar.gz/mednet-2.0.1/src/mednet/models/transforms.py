# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import numpy
import torch
import torchvision.transforms.v2
import torchvision.transforms.v2.functional
import torchvision.tv_tensors


def crop_image_to_mask(img: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Square crop image to the boundaries of a boolean mask.

    Parameters
    ----------
    img
        The image to crop, of shape channels x height x width.
    mask
        The boolean mask to use for cropping.

    Returns
    -------
        The cropped image.
    """

    if img.shape[-2:] != mask.shape[-2:]:
        raise ValueError(
            f"Image and mask must have the same size: {img.shape[-2:]} != {mask.shape[-2:]}"
        )

    h, w = img.shape[-2:]

    flat_mask = mask.flatten()
    top = flat_mask.nonzero()[0] // w
    bottom = h - (torch.flip(flat_mask, dims=(0,)).nonzero()[0] // w)

    flat_transposed_mask = torch.transpose(mask, 1, 2).flatten()
    left = flat_transposed_mask.nonzero()[0] // h
    right = w - (torch.flip(flat_transposed_mask, dims=(0,)).nonzero()[0] // h)

    return img[:, top:bottom, left:right]


def square_center_pad(img: torch.Tensor, size: typing.Any) -> torch.Tensor:
    """Return a squared version of the image, centered on a canvas padded with
    zeros.

    Parameters
    ----------
    img
        The tensor to be transformed.  Expected to be in the form: ``[...,
        [1,3], H, W]`` (i.e. arbitrary number of leading dimensions).
    size
        Height and width of the image.

    Returns
    -------
        Transformed tensor, guaranteed to be square (ie. equal height and
        width).
    """

    height, width = size
    maxdim = numpy.max([height, width])

    # padding
    left = (maxdim - width) // 2
    top = (maxdim - height) // 2
    right = maxdim - width - left
    bottom = maxdim - height - top

    return torchvision.transforms.v2.functional.pad(
        img,
        [left, top, right, bottom],
        0,
        "constant",
    )


class SquareCenterPad(torchvision.transforms.v2.Transform):
    """Transform to a squared version of the image, centered on a canvas padded
    with zeros.
    """

    def __init__(self):
        super().__init__()

    def transform(self, inpt: typing.Any, params: dict[str, typing.Any]) -> typing.Any:
        del params  # denote unused parameter
        match type(inpt):
            case (
                torch.Tensor
                | torchvision.tv_tensors.Image
                | torchvision.tv_tensors.Mask
            ):
                return square_center_pad(inpt, inpt.shape[-2:])
            case torchvision.tv_tensors.BoundingBoxes:
                return square_center_pad(inpt, inpt.canvas_size)
            case _:
                raise NotImplementedError(f"Support for type {type(inpt)} is missing")
