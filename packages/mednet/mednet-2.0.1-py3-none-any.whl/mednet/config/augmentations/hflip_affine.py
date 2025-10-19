# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Horizontal flipping (p=50%) followed by simple affine augmentations."""

from .affine import augmentations as _affine
from .hflip import augmentations as _hflip

augmentations = _hflip + _affine
