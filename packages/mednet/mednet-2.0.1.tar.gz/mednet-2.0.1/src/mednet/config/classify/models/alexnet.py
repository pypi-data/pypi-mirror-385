# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`AlexNet network architecture <alexnet-pytorch_>`_, to be trained from scratch."""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.alexnet
import mednet.models.transforms

model = mednet.models.classify.alexnet.Alexnet(
    loss_type=torch.nn.BCEWithLogitsLoss,
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=0.001),
    pretrained=False,
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        # Alexnet requires a specific input size that works for its avgpool
        # layer, which expects to downsample the input size to a multiple of 6.
        # Empirical tests show that if the input size is ..., then the
        # avgpooling layer will get these number of features:
        # 414 x 414 px -> 11 features (not OK)
        # 415 x 415 px -> 12 features (OK)
        # 446 x 446 px -> 12 features (OK)
        # 447 x 447 px -> 13 features (not OK)
        torchvision.transforms.v2.Resize(430, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
)
