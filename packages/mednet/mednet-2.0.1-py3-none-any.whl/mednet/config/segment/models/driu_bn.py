# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""DRIU with Batch Normalization Network for Vessel Segmentation.

Deep Retinal Image Understanding (DRIU), a unified framework of retinal image
analysis that provides both retinal vessel and optic disc segmentation using
deep Convolutional Neural Networks (CNNs).

Reference: :cite:p:`maninis_deep_2016`
"""

import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.losses
import mednet.models.segment.driu_bn
import mednet.models.transforms

model = mednet.models.segment.driu_bn.DRIUBN(
    loss_type=mednet.models.losses.SoftJaccardAndBCEWithLogitsLoss,
    loss_arguments=dict(alpha=0.7),  # 0.7 BCE + 0.3 Jaccard
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=0.01),
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
    pretrained=False,
)
