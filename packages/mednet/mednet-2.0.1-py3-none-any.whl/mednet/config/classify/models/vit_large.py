# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""ViT-Large, to be fine-tuned. Pre-trained on ImageNet 21K.

This configuration contains a version of ViT-Large, modified for a variable number of outputs
(defaults to 1).

N.B.: The output layer is **always** initialized from scratch.
"""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.vit
import mednet.models.transforms

model = mednet.models.classify.vit.ViT(
    architecture="vit_large_patch16_224.augreg_in21k",
    loss_type=torch.nn.BCEWithLogitsLoss,
    optimizer_type=torch.optim.AdamW,
    optimizer_arguments=dict(lr=0.0001),
    pretrained=True,
    img_size=224,
    drop_path_rate=0.1,
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(
            224,
            antialias=True,
            interpolation=torchvision.transforms.InterpolationMode.BICUBIC,
        ),
        torchvision.transforms.v2.RGB(),
    ],
)
