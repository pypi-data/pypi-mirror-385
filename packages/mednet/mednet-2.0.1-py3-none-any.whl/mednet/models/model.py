# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
import logging
import typing

import lightning.pytorch
import torch
import torch.nn
import torch.optim.lr_scheduler
import torch.optim.optimizer
import torch.utils.data
import torchvision.transforms

from ..data.datamodule import ConcatDataModule
from ..data.typing import TransformSequence
from ..utils.string import rewrap
from .typing import Checkpoint

logger = logging.getLogger(__name__)


class Model(lightning.pytorch.LightningModule):
    """Base class for models.

    Parameters
    ----------
    name
        Common name to give to models of this type.
    loss_type
        The loss to be used for training and evaluation.

        .. warning::

           The loss should be set to always return batch averages (as opposed to the
           batch sum), as our logging system expects it so.
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
        An optional sequence of torch modules containing transforms to be applied on the
        input **before** it is fed into the network.
    augmentation_transforms
        An optional sequence of torch modules containing transforms to be applied on the
        input **before** it is fed into the network.
    num_classes
        Number of outputs (classes) for this model.
    """

    def __init__(
        self,
        name: str,
        loss_type: type[torch.nn.Module] | None = None,
        loss_arguments: dict[str, typing.Any] | None = None,
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] | None = None,
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] | None = None,
        model_transforms: TransformSequence | None = None,
        augmentation_transforms: TransformSequence | None = None,
        num_classes: int = 1,
    ):
        super().__init__()

        self.name = name
        self.loss_type = loss_type
        self.train_loss_arguments = copy.deepcopy(loss_arguments or {})
        self.validation_loss_arguments = copy.deepcopy(loss_arguments or {})
        self._optimizer_type = optimizer_type
        self._optimizer_arguments = copy.deepcopy(optimizer_arguments or {})
        self._scheduler_type = scheduler_type
        self._scheduler_arguments = copy.deepcopy(scheduler_arguments or {})
        self.model_transforms = copy.deepcopy(model_transforms or [])
        self.augmentation_transforms = copy.deepcopy(augmentation_transforms or [])
        self._num_classes = num_classes

        # controls normalization and changes to the normalizer
        self._default_normalizer: typing.Callable[[torch.Tensor], torch.Tensor] = (
            lambda x: x
        )
        self._normalizer: typing.Callable[[torch.Tensor], torch.Tensor] = (
            self._default_normalizer
        )

        # initializes losses from input arguments
        self.configure_losses()

    @property
    def augmentation_transforms(self) -> torchvision.transforms.Compose:
        return self._augmentation_transforms

    @augmentation_transforms.setter
    def augmentation_transforms(self, v: TransformSequence) -> None:
        self._augmentation_transforms = torchvision.transforms.Compose(v)

        if len(v) != 0:
            transforms_str = ", ".join(
                [
                    f"{type(k).__module__}.{str(k)}"
                    for k in self._augmentation_transforms.transforms
                ]
            )
            logger.info(f"Data augmentations: {transforms_str}")
        else:
            logger.info("Data augmentations: None")

    @property
    def num_classes(self) -> int:
        """Number of outputs (classes) for this model.

        Returns
        -------
        int
            The number of outputs supported by this model.
        """
        return self._num_classes

    @num_classes.setter
    def num_classes(self, v: int) -> None:
        # on this top-level class, we do not know how to affect the number of output
        # classes supported by all possible models.
        if self._num_classes != v:
            raise NotImplementedError(
                f"Cannot reset number of classes to `{v}` for model `{self.name}`."
            )

    @property
    def normalizer(self) -> typing.Callable[[torch.Tensor], torch.Tensor]:
        """Normalizer for input images.

        Returns
        -------
            Callable (typically a :py:class:`torch.nn.Module`) that takes the input
            tensor to be normalized and returns its normalized version.
        """
        return self._normalizer

    @normalizer.setter
    def normalizer(self, v: typing.Callable[[torch.Tensor], torch.Tensor]) -> None:
        if self._normalizer != self._default_normalizer:
            raise RuntimeError(
                "Attempt to reset input normalizer after non-default initialization."
            )
        self._normalizer = v

    def normalizer_is_set(self) -> bool:
        """Tell if a normalizer different than the default (NOOP) was set.

        Returns
        -------
            ``True`` if a normalizer different than the default (NOOP) was set.  Else,
            returns ``False``.
        """
        return self._normalizer != self._default_normalizer

    def set_normalizer_from_dataloader(
        self, dataloader: torch.utils.data.DataLoader
    ) -> None:
        """Initialize the input normalizer for the current model.

        Sets-up a z-normalization scheme based on the input dataloader samples.

        Parameters
        ----------
        dataloader
            A torch Dataloader from which to compute the mean and std.
        """
        from .normalizer import make_z_normalizer

        logger.info("Computing z-norm input normalization from dataloader.")
        self._normalizer = make_z_normalizer(dataloader)

    def on_save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Perform actions during checkpoint saving (called by lightning).

        Called by Lightning when saving a checkpoint to give you a chance to store
        anything else you might want to save. Use on_load_checkpoint() to restore what
        additional data is saved here.

        Parameters
        ----------
        checkpoint
            The checkpoint to save.
        """

        if self.normalizer_is_set():
            # we need to save as this is NOT the NOOP function we typically attach
            checkpoint["normalizer"] = self._normalizer

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Perform actions during model loading (called by lightning).

        If you saved something with on_save_checkpoint() this is your chance to restore
        this.

        Parameters
        ----------
        checkpoint
            The loaded checkpoint.
        """

        normalizer = checkpoint.get("normalizer")
        if normalizer is None:
            self._normalizer = self._default_normalizer
        else:
            self._normalizer = normalizer
            logger.info("Restored input normalizer from checkpoint.")

        super().on_load_checkpoint(typing.cast(typing.Any, checkpoint))

    def balance_losses(self, datamodule: ConcatDataModule) -> None:
        """Balance the loss based on the distribution of positives.

        This function will balance the loss with considering the targets in the
        datamodule. Only works if the loss supports it (i.e. contains a ``pos_weight``
        attribute).

        Parameters
        ----------
        datamodule
            Instance of a datamodule from where targets will be loaded.
        """

        if self.loss_type is None:
            logger.info("No loss configured to be balanced.")
            return

        if issubclass(self.loss_type, torch.nn.BCEWithLogitsLoss):
            logger.info("Applying train/valid loss balancing...")
            from .losses import pos_weight_for_bcewithlogitsloss

            # special case for BCEWithLogitsLoss, which requires configuration
            train_loss_args, valid_loss_args = pos_weight_for_bcewithlogitsloss(
                datamodule
            )
            self.train_loss_arguments.update(train_loss_args)
            self.validation_loss_arguments.update(valid_loss_args)

        elif hasattr(self.loss_type, "get_arguments_from_datamodule"):
            logger.info("Applying train/valid loss balancing...")
            # it is one of our custom losses that knows how to self-configure
            train_loss_args, valid_loss_args = (
                self.loss_type.get_arguments_from_datamodule(datamodule)
            )
            self.train_loss_arguments.update(train_loss_args)
            self.validation_loss_arguments.update(valid_loss_args)

        else:
            logger.warning(
                rewrap(
                    f"""Loss `{self.loss_type}` is not supported and will not
                    be balanced."""
                )
            )

        # calls super class to continue the loss configuration
        self.configure_losses()

    def configure_losses(self) -> None:
        """Create loss objects for train and validation."""

        if self.loss_type is None:
            logger.debug("No loss to configure.")
            return

        logger.info(f"Configuring train loss ({self.train_loss_arguments})...")
        self.train_loss = self.loss_type(**self.train_loss_arguments)
        logger.info(
            f"Configuring validation loss ({self.validation_loss_arguments})..."
        )
        self.validation_loss = self.loss_type(**self.validation_loss_arguments)

    def configure_optimizers(self):
        """Configure optimizers.

        Returns
        -------
            The configured optimizer, or a tuple containing the optimizer and a
            scheduler, in case one is present.
        """

        optimizer = self._optimizer_type(self.parameters(), **self._optimizer_arguments)

        if self._scheduler_type is None:
            logger.debug("No scheduler to be configured.")
            return optimizer

        scheduler = self._scheduler_type(optimizer, **self._scheduler_arguments)
        return [optimizer], [scheduler]

    def to(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        """Move model, augmentations and losses to specified device.

        Refer to the method :py:meth:`torch.nn.Module.to` for details.

        Parameters
        ----------
        *args
            Parameter forwarded to the underlying implementations.
        **kwargs
            Parameter forwarded to the underlying implementations.

        Returns
        -------
            Self.
        """

        super().to(*args, **kwargs)

        self._augmentation_transforms = torchvision.transforms.Compose(
            [
                k.to(*args, **kwargs)
                for k in self._augmentation_transforms.transforms
                if hasattr(k, "to")
            ]
        )

        if self.loss_type is not None:
            self.train_loss.to(*args, **kwargs)
            self.validation_loss.to(*args, **kwargs)

        return self

    def forward(self, *args, **kwargs):
        del args, kwargs  # satisfies linter
        raise NotImplementedError

    def training_step(self, batch, batch_idx):
        del batch, batch_idx  # satisfies linter
        raise NotImplementedError(
            "You cannot use the base model without implementing the training_step()"
        )

    def validation_step(self, batch, batch_idx, dataloader_idx=0):
        del batch_idx, dataloader_idx  # satisfies linter

        # debug code to inspect images by eye:
        # from torchvision.transforms.v2.functional import to_pil_image
        # for k in batch["image"]:
        #    to_pil_image(k).show()
        #    __import__("pdb").set_trace()

        return self.validation_loss(self(batch["image"]), batch["target"])

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        del batch_idx, dataloader_idx  # satisfies linter

        # debug code to inspect images by eye:
        # from torchvision.transforms.v2.functional import to_pil_image
        # for k in batch["image"]:
        #    to_pil_image(k).show()
        #    __import__("pdb").set_trace()

        return torch.sigmoid(self(batch["image"]))
