# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""ViT-Large model configuration for fine-tuning with LoRA. Pre-trained on ImageNet 21K.

This configuration adapts the standard ViT-Large architecture using the PEFT library
to apply LoRA to the attention layers. The classification head is also set as trainable
for fine-tuning.

N.B.: The output layer is **always** initialized from scratch.
"""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.vit
import mednet.models.transforms
from mednet.config.peft import get_lora_config

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
    peft_config=get_lora_config(
        target_modules=r".*\.attn\.qkv",
        modules_to_save=["head"],
    ),
)
