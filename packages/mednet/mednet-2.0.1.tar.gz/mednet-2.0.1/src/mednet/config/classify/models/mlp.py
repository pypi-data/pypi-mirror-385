# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feedforward shallow MLP for binary classification.

Simple feedforward MLP taking multiple inputs and generating a single
output (e.g. to predict active TB presence from radiological finding
estimates).
"""

from mednet.models.classify.mlp import MultiLayerPerceptron

model = MultiLayerPerceptron()
