# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Functions to compute normalisation factors based on dataloaders."""

import logging

import torch
import torch.nn
import torch.utils.data
import torchvision.transforms
import tqdm

logger = logging.getLogger(__name__)


def make_z_normalizer(
    dataloader: torch.utils.data.DataLoader,
) -> torchvision.transforms.Normalize:
    """Compute mean and standard deviation from a dataloader.

    This function will input a dataloader, and compute the mean and standard
    deviation by image channel.  It will work for both monochromatic, and color
    inputs with 2, 3 or more color planes.

    Parameters
    ----------
    dataloader
        A torch Dataloader from which to compute the mean and std.

    Returns
    -------
        An initialized normalizer.
    """

    # Peek the number of channels of batches in the data loader
    batch = next(iter(dataloader))
    channels = batch["image"].shape[1]

    # Initialises accumulators
    mean = torch.zeros(channels, dtype=batch["image"].dtype)
    var = torch.zeros(channels, dtype=batch["image"].dtype)
    num_images = 0

    # Evaluates mean and standard deviation
    for batch in tqdm.tqdm(dataloader, unit="batch"):
        data = batch["image"]
        data = data.view(data.size(0), data.size(1), -1)

        num_images += data.size(0)
        mean += data.mean(2).sum(0)
        var += data.var(2).sum(0)

    mean /= num_images
    var /= num_images
    std = torch.sqrt(var)

    return torchvision.transforms.Normalize(mean, std)


def make_imagenet_normalizer() -> torchvision.transforms.Normalize:
    """Return the stock ImageNet normalisation weights from torchvision.

    The weights are wrapped in a torch module.  This normalizer only works for
    **RGB (color) images**.

    Returns
    -------
        An initialized normalizer.
    """

    return torchvision.transforms.Normalize(
        (0.485, 0.456, 0.406),
        (0.229, 0.224, 0.225),
    )


def make_cocov1_normalizer() -> torchvision.transforms.Normalize:
    """Return the stock COCO v1 normalisation weights from torchvision.

    The weights are wrapped in a torch module.  This normalizer only works for
    **RGB (color) images**.

    Returns
    -------
        An initialized normalizer.
    """

    return torchvision.transforms.Normalize(
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
    )


def make_standard_normalizer() -> torchvision.transforms.Normalize:
    """Return a standard Normalizer with mean and standard deviation
    equal to 0.5 on all channels.

    The weights are wrapped in a torch module.  This normalizer only works for
    **RGB (color) images**.

    Returns
    -------
        An initialized normalizer.
    """
    return torchvision.transforms.Normalize(
        (0.5, 0.5, 0.5),
        (0.5, 0.5, 0.5),
    )
