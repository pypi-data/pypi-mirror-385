# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Vision Transformer architecture implemented with `timm <https://huggingface.co/timm>`_."""

import logging
import typing
from typing import Literal

import timm
import torch
import torch.nn
import torch.optim.optimizer
import torch.utils.data
import torchvision.transforms
from peft import (
    PeftConfig,
    get_peft_model,
    get_peft_model_state_dict,
    set_peft_model_state_dict,
)

from ...data.typing import TransformSequence
from ..typing import Checkpoint
from .model import Model
from .typing import ViTArchitectures

logger = logging.getLogger(__name__)


class ViT(Model):
    """Vision Transformer architecture implemented with `timm <https://huggingface.co/timm>`_.

    Parameters
    ----------
    loss_type
        The loss to be used for training and evaluation.

        .. warning::

           The loss should be set to always return batch averages (as opposed
           to the batch sum), as our logging system expects it so.
    loss_arguments
        Arguments to the loss.
    optimizer_type
        The type of optimizer to use for training.
    optimizer_arguments
        Arguments to the optimizer after ``params``.
    scheduler_type
        The type of scheduler to use for training.
    scheduler_arguments
        Arguments to the scheduler after ``params``.
    model_transforms
        An optional sequence of torch modules containing transforms to be
        applied on the input **before** it is fed into the network.
    augmentation_transforms
        An optional sequence of torch modules containing transforms to be
        applied on the input **before** it is fed into the network.
    architecture
        Name of the ViT architecture to instantiate (`Hugging Face models <https://huggingface.co/models>`_).
    pretrained
        If set to True, loads pretrained model weights during initialization,
        else trains a new model (random initialization).
    img_size
        Input image size.
    drop_path_rate
        Stochastic depth drop rate, acts like dropout but at the block level.
    drop_rate
        Classifier (head) dropout rate.
    global_pool
        Type of global pooling for final sequence (default: 'token').
    peft_config
        The configuration object (PeftConfig) containing the parameters of the Peft model.
        (i.e. `LoraConfig <https://huggingface.co/docs/peft/v0.15.0/en/package_reference/lora#peft.LoraConfig>`_).
    num_classes
        Number of outputs (classes) for this model.
    """

    def __init__(
        self,
        loss_type: type[torch.nn.Module] = torch.nn.BCEWithLogitsLoss,
        loss_arguments: dict[str, typing.Any] | None = None,
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] | None = None,
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] | None = None,
        model_transforms: TransformSequence | None = None,
        augmentation_transforms: TransformSequence | None = None,
        architecture: ViTArchitectures = "vit_base_patch16_224.augreg_in21k",
        pretrained: bool = True,
        img_size: int = 224,
        drop_path_rate: float = 0.0,
        drop_rate: float = 0.0,
        global_pool: Literal["", "avg", "avgmax", "max", "token", "map"] = "token",
        peft_config: PeftConfig | None = None,
        num_classes: int = 1,
    ):
        super().__init__(
            name=architecture,
            loss_type=loss_type,
            loss_arguments=loss_arguments,
            optimizer_type=optimizer_type,
            optimizer_arguments=optimizer_arguments,
            scheduler_type=scheduler_type,
            scheduler_arguments=scheduler_arguments,
            model_transforms=model_transforms,
            augmentation_transforms=augmentation_transforms,
            num_classes=num_classes,
        )

        self.architecture = architecture
        self.pretrained = pretrained
        self.img_size = img_size
        self.global_pool = global_pool
        self.peft_config = peft_config

        # Load pretrained model weights from timm
        if self.pretrained:
            logger.info(f"Loading pretrained `{self.name}` model weights from timm.")

        self.model = timm.create_model(
            self.architecture,
            img_size=(self.img_size, self.img_size),
            drop_path_rate=drop_path_rate,
            drop_rate=drop_rate,
            global_pool=self.global_pool,
            num_classes=num_classes,
            pretrained=self.pretrained,
        )

        # Set normalizer according to the model's data configuration
        data_config = timm.data.resolve_model_data_config(self.model)
        Model.normalizer.fset(  # type: ignore[attr-defined]
            self,
            torchvision.transforms.Normalize(
                mean=data_config["mean"],
                std=data_config["std"],
            ),
        )

        if self.peft_config is not None:
            self.model = get_peft_model(
                model=self.model,
                peft_config=self.peft_config,
            )
            # By default, when you call trainer.fit, Lightning internally calls load_state_dict() with strict=True.
            # This strict loading fails if the checkpoint's state_dict is modified, as happens with PEFT adapters.
            # To avoid errors when loading such checkpoints, we disable strict loading here.
            self.strict_loading = False

    @Model.num_classes.setter  # type: ignore[attr-defined]
    def num_classes(self, v: int) -> None:
        if self.num_classes != v:
            logger.info(
                f"Resetting `{self.name}` output classifier layer weights due "
                f"to a change in output size ({self.num_classes} -> {v})"
            )

            if self.global_pool in ("avg", "avgmax", "max"):
                # For this type of pooling timm moves the final norm layer
                # after the pool operation and calls it fc_norm
                in_features = self.model.fc_norm.normalized_shape[0]
            else:
                in_features = self.model.norm.normalized_shape[0]
            # Instantiate the new classification head
            new_head = torch.nn.Linear(in_features=in_features, out_features=v)

            if self.peft_config is None:
                self.model.head = new_head
            else:
                # In a PeftModel self.model.head is a ModulesToSaveWrapper,
                # an intern class of the peft library (check peft.utils.other).
                # To modify it you simply change the original_module attribute
                # with the new classification head and call the .update() method.
                self.model.head.original_module = new_head
                self.model.head.update("default")
            self._num_classes = v

    def on_save_checkpoint(self, checkpoint: Checkpoint):
        # It is necessary to save this information inside the checkpoint of the model
        # because in the 'predict' script you call model=type(model).load_from_checkpoint(...).
        # When you call it you are reinstatiating the model by creating a new one with
        # default arguments.
        checkpoint["architecture"] = self.architecture
        checkpoint["pretrained"] = self.pretrained
        checkpoint["img_size"] = self.img_size
        checkpoint["global_pool"] = self.global_pool
        checkpoint["peft_config"] = self.peft_config

        if self.peft_config is not None:
            # No need to save the whole model's weights, just the adapter's weights
            # and, when specified in the peft_config object, the 'modules_to_save', which
            # are the modules apart from adapter layers to be set as trainable and saved
            # in the final checkpoint
            checkpoint["state_dict"] = get_peft_model_state_dict(self.model)

        super().on_save_checkpoint(checkpoint)

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        # could need interpolation of pos embed

        # reset number of output classes if need be
        head_key = (
            "model.head.bias"
            if checkpoint["peft_config"] is None
            else "base_model.model.head.bias"
        )
        self.num_classes = checkpoint["state_dict"][head_key].shape[0]

        # Retrieve specific information of the original model
        self.architecture = checkpoint["architecture"]
        self.name = self.architecture
        self.pretrained = checkpoint["pretrained"]
        self.img_size = checkpoint["img_size"]
        self.global_pool = checkpoint["global_pool"]
        self.peft_config = checkpoint["peft_config"]

        # Correct the model if need to be
        self.model = timm.create_model(
            self.architecture,
            img_size=(self.img_size, self.img_size),
            global_pool=self.global_pool,
            num_classes=self.num_classes,
            pretrained=self.pretrained,
        )

        if self.peft_config is not None:
            self.model = get_peft_model(
                model=self.model,
                peft_config=self.peft_config,
            )
            # load adapter's weights into the adapter layers
            _ = set_peft_model_state_dict(
                model=self.model, peft_model_state_dict=checkpoint["state_dict"]
            )

        # perform routine checkpoint loading
        super().on_load_checkpoint(checkpoint)

    def forward(self, x):
        x = self.normalizer(x)
        return self.model(x)
