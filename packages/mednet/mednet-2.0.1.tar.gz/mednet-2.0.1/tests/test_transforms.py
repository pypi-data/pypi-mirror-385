# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for transforms."""

import numpy
import PIL.Image
import torch
import torchvision.transforms.v2.functional as F  # noqa: N812
import torchvision.tv_tensors

import mednet.data.augmentations
import mednet.models.transforms


def test_crop_mask():
    original_tensor_size = (3, 50, 100)
    original_mask_size = (1, 50, 100)
    slice_ = (slice(None), slice(10, 30), slice(50, 70))

    tensor = torch.rand(original_tensor_size)
    mask = torch.zeros(original_mask_size)
    mask[slice_] = 1

    cropped_tensor = mednet.models.transforms.crop_image_to_mask(tensor, mask)

    assert cropped_tensor.shape == (3, 20, 20)
    assert torch.all(cropped_tensor.eq(tensor[slice_]))


def test_elastic_deformation(datadir):
    # Get a raw sample without deformation
    raw_without_deformation = PIL.Image.open(
        datadir / "raw_without_elastic_deformation.png"
    )
    raw_without_deformation = F.to_dtype(
        F.to_image(raw_without_deformation), torch.float32, scale=True
    )

    # Elastic deforms the raw
    ed = mednet.data.augmentations.ElasticDeformation(seed=100)
    raw_deformed = ed(raw_without_deformation)
    raw_deformed = F.to_pil_image(raw_deformed)
    # uncomment to save a new reference if required
    # raw_deformed.save(datadir / "raw_with_elastic_deformation.png")

    # Get the same sample already deformed (with seed=100)
    raw_2 = PIL.Image.open(datadir / "raw_with_elastic_deformation.png")
    raw_2 = F.to_pil_image(F.to_dtype(F.to_image(raw_2), torch.float32, scale=True))

    numpy.testing.assert_array_equal(numpy.asarray(raw_deformed), numpy.asarray(raw_2))


def test_square_center_pad():
    # is this transform functionally correct?

    tensor = torch.rand((3, 50, 100)).float()
    x = mednet.models.transforms.square_center_pad(tensor, tensor.shape[-2:])
    assert x.shape == (3, 100, 100)
    assert (tensor == x[:, 25:75, :]).all()
    assert (x[:, 0:25, :] == 0.0).all()
    assert (x[:, 75:, :] == 0.0).all()

    tensor = torch.rand((3, 12, 10)).float()
    x = mednet.models.transforms.square_center_pad(tensor, tensor.shape[-2:])
    assert x.shape == (3, 12, 12)
    assert (tensor == x[:, :, 1:11]).all()
    assert (x[:, :, 0] == 0.0).all()
    assert (x[:, :, 11] == 0.0).all()


def test_square_center_pad_tv_v2():
    # does this transform conform to the torchvision v2 transform API?

    tensor = torch.rand((3, 50, 100)).float()

    transform = mednet.models.transforms.SquareCenterPad()
    x = transform(tensor)

    assert isinstance(x, torch.Tensor)
    assert not isinstance(x, torchvision.tv_tensors.Image)
    assert x.shape == (3, 100, 100)
    assert (tensor == x[:, 25:75, :]).all()
    assert (x[:, 0:25, :] == 0.0).all()
    assert (x[:, 75:, :] == 0.0).all()

    image = torchvision.tv_tensors.Image(tensor)

    xi = transform(image)
    assert isinstance(xi, torchvision.tv_tensors.Image)
    assert xi.shape == (3, 100, 100)
    assert (tensor == xi[:, 25:75, :]).all()
    assert (xi[:, 0:25, :] == 0.0).all()
    assert (xi[:, 75:, :] == 0.0).all()

    mask = torchvision.tv_tensors.Mask(tensor)

    xm = transform(mask)
    assert isinstance(xm, torchvision.tv_tensors.Mask)
    assert xi.shape == (3, 100, 100)
    assert (tensor == xi[:, 25:75, :]).all()
    assert (xi[:, 0:25, :] == 0.0).all()
    assert (xi[:, 75:, :] == 0.0).all()

    bboxes = torchvision.tv_tensors.BoundingBoxes(
        [[10, 10, 30, 30]], format="XYXY", canvas_size=tensor.shape[-2:]
    )

    xb = transform(bboxes)
    assert isinstance(xb, torchvision.tv_tensors.BoundingBoxes)
    assert xb.canvas_size == (100, 100)
    assert (xb == torch.Tensor([[10, 10 + 25, 30, 30 + 25]])).all()
