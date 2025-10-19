# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Elastic deformation with 80% probability.

This sole data augmentation was proposed by Pasa in the article "Efficient Deep
Network Architectures for Fast Chest X-Ray Tuberculosis Screening and
Visualization".

Reference: :cite:p:`pasa_efficient_2019`
"""

from ...data.augmentations import ElasticDeformation

augmentations = [ElasticDeformation(p=0.8)]
