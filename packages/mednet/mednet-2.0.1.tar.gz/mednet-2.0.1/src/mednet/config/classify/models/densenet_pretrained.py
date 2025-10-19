# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""DenseNet_, to be fine-tuned. Pre-trained on ImageNet_.

This configuration contains a version of DenseNet_ (c.f. `TorchVision's
page <alexnet_pytorch_>`), modified for a variable number of outputs
(defaults to 1).

N.B.: The output layer is **always** initialized from scratch.
"""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.densenet
import mednet.models.transforms

model = mednet.models.classify.densenet.Densenet(
    loss_type=torch.nn.BCEWithLogitsLoss,
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=0.0001),
    pretrained=True,
    dropout=0.1,
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
)
