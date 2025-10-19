# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple CNN for 3D image classification, to be trained from scratch."""

from torch.nn import BCEWithLogitsLoss
from torch.optim import Adam

from mednet.models.classify.cnn3d import Conv3DNet

model = Conv3DNet(
    loss_type=BCEWithLogitsLoss,
    optimizer_type=Adam,
    optimizer_arguments=dict(lr=8e-5),
)
