# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""HED Network for Segmentation.

Reference: :cite:p:`xie_holistically-nested_2015`
"""

import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.losses
import mednet.models.segment.hed
import mednet.models.transforms

model = mednet.models.segment.hed.HED(
    loss_type=mednet.models.losses.MultiLayerSoftJaccardAndBCELogitsLoss,
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
