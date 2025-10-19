# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple CNN for Tuberculosis Detection, to be trained from scratch.

Implementation of the model architecture proposed by F. Pasa in the article
"Efficient Deep Network Architectures for Fast Chest X-Ray Tuberculosis
Screening and Visualization".

Reference: :cite:p:`pasa_efficient_2019`
"""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.pasa
import mednet.models.transforms

model = mednet.models.classify.pasa.Pasa(
    loss_type=torch.nn.BCEWithLogitsLoss,
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=8e-5),
    model_transforms=[
        torchvision.transforms.v2.Grayscale(),
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
    ],
    augmentation_transforms=[],
)
