# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""U-Net for image segmentation.

U-Net is a convolutional neural network that was developed for biomedical image
segmentation at the Computer Science Department of the University of Freiburg,
Germany.  The network is based on the fully convolutional network (FCN) and its
architecture was modified and extended to work with fewer training images and
to yield more precise segmentations.

Reference: :cite:p:`navab_u-net_2015`
"""

import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.losses
import mednet.models.segment.unet
import mednet.models.transforms

model = mednet.models.segment.unet.Unet(
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
