# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Little W-Net for image segmentation.

The Little W-Net architecture contains roughly around 70k parameters and
closely matches (or outperforms) other more complex techniques.

Reference: :cite:p:`galdran_state---art_2022`
"""

import torch.optim
import torch.optim.lr_scheduler
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.losses
import mednet.models.segment.lwnet
import mednet.models.transforms

max_lr = 0.01  # start
min_lr = 1e-08  # valley
# Original strategy: https://github.com/agaldran/lwnet/blob/master/train_cyclical.py#L298
# About 20 * len(train-data-loader)
cycle = 100  # 1/2 epochs for a complete scheduling cycle

model = mednet.models.segment.lwnet.LittleWNet(
    loss_type=mednet.models.losses.MultiLayerBCELogitsLossWeightedPerBatch,
    loss_arguments=dict(),
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=max_lr),
    scheduler_type=torch.optim.lr_scheduler.CosineAnnealingLR,
    scheduler_arguments=dict(T_max=cycle, eta_min=min_lr),
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
)
