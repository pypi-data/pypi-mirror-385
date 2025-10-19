# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Color/grayscale jitter 20% transformations."""

import torchvision.transforms

augmentations = [
    torchvision.transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2,
    )
]
