# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Horizontal flip with 50% probability."""

import torchvision.transforms

augmentations = [torchvision.transforms.RandomHorizontalFlip(p=0.5)]
