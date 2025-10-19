# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Support code to adapt existing `MobileNetV2 pytorch model <mobilenetv2-pytorch_>`_ functionality to U-Net style network for segmentation."""

import torchvision.models
import torchvision.models.mobilenetv2
from torch.hub import load_state_dict_from_url


class MobileNetV24Segmentation(torchvision.models.mobilenetv2.MobileNetV2):
    """Adaptation of `MobileNetV2 pytorch model <mobilenetv2-pytorch_>`_ to U-Net style network for segmentation.

    This version of MobileNetV2 is slightly modified so it can be used through
    torchvision's API.  It outputs intermediate features which are normally not
    output by the base MobileNetV2 implementation, but are required for
    segmentation operations.

    Parameters
    ----------
    *args
        Arguments to be passed to the parent MobileNetV2 model.
    **kwargs
        Keyword arguments to be passed to the parent MobileNetV2 model.

        * ``return_features`` (:py:class:`list`): An optional list of integers indicating
          the feature layers to be returned from the original module.
    """

    def __init__(self, *args, **kwargs):
        self._return_features = kwargs.pop("return_features")
        super().__init__(*args, **kwargs)

    def forward(self, x):
        outputs = []
        # hw of input, needed for DRIU and HED
        outputs.append(x.shape[2:4])
        outputs.append(x)
        for index, m in enumerate(self.features):
            x = m(x)
            # extract layers
            if index in self._return_features:
                outputs.append(x)
        return outputs


def mobilenet_v2_for_segmentation(pretrained=False, progress=True, **kwargs):
    """Create MobileNetV2 model for segmentation task.

    Parameters
    ----------
    pretrained
        If True, uses MobileNetV2 pretrained weights.
    progress
        If True, shows a progress bar when downloading the pretrained weights.
    **kwargs
        Keyword arguments to be passed to the parent MobileNetV2 model.

        * ``return_features`` (:py:class:`list`): An optional list of integers indicating
          the feature layers to be returned from the original module.

    Returns
    -------
        Instance of the MobileNetV2 model for segmentation.
    """

    model = MobileNetV24Segmentation(**kwargs)

    if pretrained:
        state_dict = load_state_dict_from_url(
            torchvision.models.mobilenetv2.MobileNet_V2_Weights.DEFAULT.url,
            progress=progress,
        )
        model.load_state_dict(state_dict)

    # erase MobileNetV2 head (for classification), not used for segmentation
    delattr(model, "classifier")

    return_features = kwargs.get("return_features")
    if return_features is not None:
        model.features = model.features[: (max(return_features) + 1)]

    return model


mobilenet_v2_for_segmentation.__doc__ = torchvision.models.mobilenetv2.__doc__
