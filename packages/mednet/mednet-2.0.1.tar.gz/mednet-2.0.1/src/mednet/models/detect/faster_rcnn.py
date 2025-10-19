# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Faster R-CNN object detection (and classification) network architecture, from :cite:p:`ren_faster_2017`."""

import logging
import typing

import torch
import torch.nn
import torch.optim
import torch.optim.lr_scheduler
import torch.optim.optimizer
import torch.utils.data
import torchvision.models as models

from ...data.typing import TransformSequence
from ..typing import Checkpoint
from .model import Model

logger = logging.getLogger(__name__)


class FasterRCNN(Model):
    """Faster R-CNN object detection (and classification) network architecture, from :cite:p:`ren_faster_2017`.

    Parameters
    ----------
    optimizer_type
        The type of optimizer to use for training.
    optimizer_arguments
        Arguments to the optimizer after ``params``.
    scheduler_type
        The type of scheduler to use for training.
    scheduler_arguments
        Arguments to the scheduler after ``params``.
    model_transforms
        An optional sequence of torch modules containing transforms to be applied on the
        input **before** it is fed into the network.
    augmentation_transforms
        An optional sequence of torch modules containing transforms to be applied on the
        input **before** it is fed into the network.
    pretrained
        If set to True, loads pretrained model weights during initialization, else
        trains a new model.
    num_classes
        Number of outputs (classes) for this model. Do not account for the background
        (we compensate internally).
    variant
        One of the torchvision supported variants.
    """

    def __init__(
        self,
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.SGD,
        optimizer_arguments: dict[str, typing.Any] = dict(
            lr=0.005, momentum=0.9, weight_decay=0.0005
        ),
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler]
        | None = torch.optim.lr_scheduler.StepLR,
        scheduler_arguments: dict[str, typing.Any] = dict(step_size=3, gamma=0.1),
        model_transforms: TransformSequence | None = None,
        augmentation_transforms: TransformSequence | None = None,
        pretrained: bool = False,
        num_classes: int = 1,
        variant: typing.Literal[
            "resnet50-v1", "resnet50-v2", "mobilenetv3-large", "mobilenetv3-small"
        ] = "mobilenetv3-small",
    ):
        super().__init__(
            name=f"faster-rcnn[{variant}]",
            loss_type=None,
            loss_arguments=None,
            optimizer_type=optimizer_type,
            optimizer_arguments=optimizer_arguments,
            scheduler_type=scheduler_type,
            scheduler_arguments=scheduler_arguments,
            model_transforms=model_transforms,
            augmentation_transforms=augmentation_transforms,
            num_classes=num_classes,
        )

        self.pretrained = pretrained
        self.variant = variant

        # Load pretrained model
        weights = None
        if pretrained:
            from ..normalizer import make_cocov1_normalizer

            Model.normalizer.fset(self, make_cocov1_normalizer())  # type: ignore[attr-defined]

            logger.info(f"Loading pretrained `{self.name}` model weights")
            match self.variant:
                case "resnet50-v1":
                    weights = "FasterRCNN_ResNet50_FPN_Weights.COCO_V1"
                case "resnet50-v2":
                    weights = "FasterRCNN_ResNet50_FPN_V2_Weights.COCO_V1"
                case "mobilenetv3-large":
                    weights = "FasterRCNN_MobileNet_V3_Large_FPN_Weights.COCO_V1"
                case "mobilenetv3-small":
                    weights = "FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.COCO_V1"

        match self.variant:
            case "resnet50-v1":
                self.model = models.detection.fasterrcnn_resnet50_fpn(weights=weights)
            case "resnet50-v2":
                self.model = models.detection.fasterrcnn_resnet50_fpn_v2(
                    weights=weights
                )
            case "mobilenetv3-large":
                self.model = models.detection.fasterrcnn_mobilenet_v3_large_fpn(
                    weights=weights
                )
            case "mobilenetv3-small":
                self.model = models.detection.fasterrcnn_mobilenet_v3_large_320_fpn(
                    weights=weights
                )

        # Instantiates model and adapts output features
        self.num_classes = num_classes

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        # Faster R-CNN models will have num_classes + 1 outputs accounting for the
        # background
        v += 1

        if self.model.roi_heads.box_predictor.cls_score.out_features != v:
            if self.pretrained:
                logger.info(
                    f"Resetting `{self.name}` pretrained classifier "
                    f"layer weights due to change in output size "
                    f"({self.model.roi_heads.box_predictor.cls_score.out_features} -> {v})"
                )
            self.model.roi_heads.box_predictor = (
                models.detection.faster_rcnn.FastRCNNPredictor(
                    self.model.roi_heads.box_predictor.cls_score.in_features, v
                )
            )
        self._num_classes = v

    def on_save_checkpoint(self, checkpoint: Checkpoint) -> None:
        checkpoint["variant"] = self.variant
        super().on_save_checkpoint(checkpoint)

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        # setup model type
        self.variant = checkpoint.get("variant", "mobilenetv3-small")
        match self.variant:
            case "resnet50-v1":
                self.model = models.detection.fasterrcnn_resnet50_fpn()
            case "resnet50-v2":
                self.model = models.detection.fasterrcnn_resnet50_fpn_v2()
            case "mobilenetv3-large":
                self.model = models.detection.fasterrcnn_mobilenet_v3_large_fpn()
            case "mobilenetv3-small":
                self.model = models.detection.fasterrcnn_mobilenet_v3_large_320_fpn()

        # reset number of classes if need be
        num_classes = checkpoint["state_dict"][
            "model.roi_heads.box_predictor.cls_score.bias"
        ].shape[0]

        if num_classes != self.num_classes:
            logger.debug(
                f"Resetting number-of-output-classes at `{self.name}` model from "
                f"{self.num_classes} to {num_classes} while loading checkpoint."
            )
        self.num_classes = num_classes - 1

        super().on_load_checkpoint(checkpoint)

    def forward(
        self,
        images: list[torch.Tensor],
        targets: list[dict[str, torch.Tensor]] | None = None,
    ):
        """Forward the input tensor through the network, producing a prediction.

        Parameters
        ----------
        images
            Input images, to be analyzed or trained on.
        targets
            Targets for the current input images.  Targets should be passed only if
            *training*. It should be alist of dictionaries, each corresponding to one of
            the input images in ``images``.  Each dictionary should have two keys:
            ``boxes``, that contains the bounding boxes associated with the image, and
            ``labels``, that contains the labels associated with each bounding box.

        Returns
        -------
            A list with various dictionaries, each referring to one of the
        """
        images = [self.normalizer(k) for k in images]

        if targets is None:
            return self.model(images)

        return self.model(images, targets)

    def training_step(self, batch, batch_idx):
        del batch_idx

        # debug code to inspect images by eye:
        # from torchvision.transforms.v2.functional import to_pil_image
        # for k in batch["image"]:
        #    to_pil_image(k).show()
        #    __import__("pdb").set_trace()

        # during training, detection models __call__() take 2 lists as inputs:
        # * list of images
        # * list of dictionaries with "boxes" and "labels"
        #
        # -> model returns a Dict[Tensor] during training, containing the
        #    classification and regression losses for both the RPN and the R-CNN.
        result = self.forward(
            [k for k in self._augmentation_transforms(batch["image"])],
            [
                {"boxes": k1, "labels": k2.long()}
                for (k1, k2) in zip(
                    self._augmentation_transforms(batch["target"]), batch["labels"]
                )
            ],
        )
        return sum(result.values())

    def validation_step(self, batch, batch_idx, dataloader_idx=0):
        del batch_idx, dataloader_idx  # satisfies linter

        # need to be in "train" mode to calculate losses
        self.model.train()
        with torch.no_grad():
            result = self(
                [k for k in batch["image"]],
                [
                    {"boxes": k1, "labels": k2.long()}
                    for (k1, k2) in zip(batch["target"], batch["labels"])
                ],
            )
        return sum(result.values())

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        del batch_idx, dataloader_idx  # satisfies linter

        # debug code to inspect images by eye:
        # from torchvision.transforms.v2.functional import to_pil_image
        # for k in batch["image"]:
        #    to_pil_image(k).show()
        #    __import__("pdb").set_trace()

        # during inference, detection models __call__() take 1 list as input:
        # * list of images
        #
        # -> model returns the post-processed predictions as a
        #    list[dict[torch.Tensor]], one for each input image
        return self([k for k in batch["image"]])
