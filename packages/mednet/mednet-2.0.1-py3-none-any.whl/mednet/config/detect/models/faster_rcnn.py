# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Faster R-CNN object detection (and classification) network architecture, from :cite:p:`ren_faster_2017`."""

import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.detect.faster_rcnn
import mednet.models.losses
import mednet.models.transforms

model = mednet.models.detect.faster_rcnn.FasterRCNN(
    optimizer_type=torch.optim.SGD,
    optimizer_arguments=dict(lr=0.005, momentum=0.9, weight_decay=0.0005),
    scheduler_type=torch.optim.lr_scheduler.StepLR,
    scheduler_arguments=dict(step_size=3, gamma=0.1),
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
    pretrained=True,
    num_classes=1,
    variant="mobilenetv3-small",  # fastest testing
)
