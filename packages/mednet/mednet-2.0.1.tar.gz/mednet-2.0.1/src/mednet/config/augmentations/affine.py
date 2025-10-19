# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple affine augmentations for image analysis."""

import torchvision.transforms

augmentations = [
    torchvision.transforms.RandomAffine(
        degrees=10,
        translate=(0.1, 0.1),  # horizontal, vertical
        scale=(0.8, 1.0),  # minimum, maximum
        interpolation=torchvision.transforms.InterpolationMode.BILINEAR,
    ),
]
