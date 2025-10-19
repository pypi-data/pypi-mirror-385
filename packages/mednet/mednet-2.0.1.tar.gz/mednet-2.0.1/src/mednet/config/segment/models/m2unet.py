# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""MobileNetV2 U-Net model for image segmentation.

The MobileNetV2 architecture is based on an inverted residual structure where
the input and output of the residual block are thin bottleneck layers opposite
to traditional residual models which use expanded representations in the input
an MobileNetV2 uses lightweight depthwise convolutions to filter features in
the intermediate expansion layer.  This model implements a MobileNetV2 U-Net
model, henceforth named M2U-Net, combining the strenghts of U-Net for medical
segmentation applications and the speed of MobileNetV2 networks.

References: :cite:p:`sandler_mobilenetv2_2018`, :cite:p:`navab_u-net_2015`
"""

import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.losses
import mednet.models.segment.m2unet
import mednet.models.transforms

model = mednet.models.segment.m2unet.M2Unet(
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
