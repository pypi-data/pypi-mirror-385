# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lightning callbacks to log custom measurements."""

import logging
import time
import typing
import warnings

import lightning.pytorch
import lightning.pytorch.callbacks
import torch

from ..utils.resources import ResourceMonitor, aggregate

logger = logging.getLogger(__name__)


class LoggingCallback(lightning.pytorch.Callback):
    """Callback to log various training metrics and device information.

    Rationale:

    1. Losses are logged at the end of every batch, accumulated and handled by
       the lightning framework.
    2. Everything else is done at the end of a training or validation epoch and
       mostly concerns runtime metrics such as memory and cpu/gpu utilisation.

    Parameters
    ----------
    resource_monitor
        A monitor that watches resource usage (CPU/GPU) in a separate process
        and totally asynchronously with the code execution.
    """

    def __init__(
        self,
        resource_monitor: ResourceMonitor,
    ):
        super().__init__()

        # timers
        self._start_training_time = time.time()
        self._start_training_epoch_time = time.time()
        self._start_validation_epoch_time = time.time()

        # log accumulators for a single flush at each training cycle
        self._to_log: dict[str, float] = {}

        # helpers for CPU and GPU utilisation
        self._resource_monitor = resource_monitor
        self._max_queue_retries = 2

    def on_train_start(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
    ):
        """Execute actions when training starts (lightning callback).

        This method is executed whenever you *start* training a module.

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        """
        self._start_training_time = time.time()

    def on_train_end(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
    ):
        """Execute actions when training ends (lightning callback).

        This method is executed whenever you *end* training a module.

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        """
        pass

    def on_train_epoch_start(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
    ) -> None:
        """Execute actions when a training epoch starts (lightning callback).

        This method is executed whenever a training epoch starts.  Presumably,
        batches happen as often as possible.  You want to make this code very
        fast.  Do not log things to the terminal or the such, or do complicated
        (lengthy) calculations.

        .. warning::

           This is executed **while** you are training.  Be very succint or
           face the consequences of slow training!

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        """

        # summarizes resource usage since the last checkpoint
        # clears internal buffers and starts accumulating again.
        self._resource_monitor.clear()

        self._start_training_epoch_time = time.time()

    def on_train_epoch_end(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
    ):
        """Execute actions after a training epoch ends (lightning callback).

        This method is executed whenever a training epoch ends.  Presumably,
        epochs happen as often as possible.  You want to make this code
        relatively fast to avoid significative runtime slow-downs.

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        """

        # evaluates this training epoch total time, and log it
        epoch_time = time.time() - self._start_training_epoch_time

        self._to_log["epoch-duration-seconds/train"] = epoch_time

        if len(pl_module.trainer.lr_scheduler_configs) == 0:
            self._to_log["learning-rate"] = pl_module.optimizers().defaults["lr"]  # type: ignore
        else:
            self._to_log["learning-rate"] = pl_module.trainer.lr_scheduler_configs[
                0
            ].scheduler.get_last_lr()[0]  # type: ignore

        overall_cycle_time = time.time() - self._start_training_epoch_time
        self._to_log["cycle-time-seconds/train"] = overall_cycle_time
        self._to_log["total-execution-time-seconds"] = (
            time.time() - self._start_training_time
        )
        self._to_log["eta-seconds"] = overall_cycle_time * (
            trainer.max_epochs - trainer.current_epoch  # type: ignore
        )
        # the "step" is the tensorboard jargon for "epoch" or "batch",
        # depending on how we are logging - in a more general way, it simply
        # means the relative time step.
        self._to_log["step"] = float(trainer.current_epoch)

        # Do not log during sanity check as results are not relevant
        if not trainer.sanity_checking:
            pl_module.log_dict(self._to_log)
            self._to_log = {}

    def on_train_batch_end(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
        outputs: typing.Mapping[str, torch.Tensor],
        batch: typing.Mapping[str, typing.Any],
        batch_idx: int,
    ) -> None:
        """Execute actions after a training batch ends (lightning callback).

        This method is executed whenever a training batch ends.  Presumably,
        batches happen as often as possible.  You want to make this code very
        fast.  Do not log things to the terminal or the such, or do complicated
        (lengthy) calculations.

        .. warning::

           This is executed **while** you are training.  Be very succint or
           face the consequences of slow training!

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        outputs
            The outputs of the module's ``training_step``.
        batch
            The data that the training step received.
        batch_idx
            The relative number of the batch.
        """

        batch_size = batch["image"].shape[0]

        pl_module.log(
            "loss/train",
            outputs["loss"].item(),
            prog_bar=True,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
        )

    def on_validation_epoch_start(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
    ) -> None:
        """Execute actions before a validation batch starts (lightning callback).

        This method is executed whenever a validation batch starts.  Presumably,
        batches happen as often as possible.  You want to make this code very
        fast.  Do not log things to the terminal or the such, or do complicated
        (lengthy) calculations.

        .. warning::

           This is executed **while** you are training.  Be very succint or
           face the consequences of slow training!

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        """

        current_timestamp = time.time()

        # required because the validation epoch is started **within** the
        # training epoch START/END.
        # summarizes resource usage since the last checkpoint
        metrics = self._resource_monitor.checkpoint()

        # filter out samples not acquired during the training epoch
        metrics = [
            k
            for k in metrics
            if k["timestamp"] > self._start_training_epoch_time
            and k["timestamp"] < current_timestamp
        ]

        if not metrics:
            warnings.warn(
                f"CPU/GPU monitor worker did not provide any measures. "
                f"This can be due to the length of the monitoring interval, "
                f"currently set to {self._resource_monitor.interval}s, "
                f"compared to the time I've been accumulating measurements "
                f"({(time.time()-self._start_training_epoch_time):.1f}s). "
                f"A way this can be fixed is by reducing the monitoring "
                f"interval to a suitable value, so it allows some measures "
                f"to be performed. Note this is only possible if the time "
                f"to log a single measurement point is smaller than the "
                f"time it takes to **train** a single epoch."
            )
        else:
            for metric_name, metric_value in aggregate(metrics).items():
                self._to_log[f"{metric_name}/train"] = float(metric_value)

        self._start_validation_epoch_time = time.time()
        self._resource_monitor.clear()

    def on_validation_epoch_end(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
    ) -> None:
        """Execute actions after a validation batch ends (lightning callback).

        This method is executed whenever a validation epoch ends.  Presumably,
        epochs happen as often as possible.  You want to make this code
        relatively fast to avoid significative runtime slow-downs.

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        """

        current_timestamp = time.time()

        # summarizes resource usage since the last checkpoint
        # clears internal buffers and starts accumulating again.
        metrics = self._resource_monitor.checkpoint()

        # filter out samples not acquired during the validation epoch
        metrics = [
            k
            for k in metrics
            if k["timestamp"] > self._start_training_epoch_time
            and k["timestamp"] < current_timestamp
        ]

        if not metrics:
            warnings.warn(
                f"CPU/GPU monitor worker did not provide any measures. "
                f"This can be due to the length of the monitoring interval, "
                f"currently set to {self._resource_monitor.interval}s, "
                f"compared to the time I've been accumulating measurements "
                f"({(time.time()-self._start_validation_epoch_time):.1f}s). "
                f"A way this can be fixed is by reducing the monitoring "
                f"interval to a suitable value, so it allows some measures "
                f"to be performed. Note this is only possible if the time "
                f"to log a single measurement point is smaller than the "
                f"time it takes to **validate** a single epoch."
            )
        else:
            for metric_name, metric_value in aggregate(metrics).items():
                self._to_log[f"{metric_name}/validation"] = float(metric_value)

        epoch_time = time.time() - self._start_validation_epoch_time
        self._to_log["epoch-duration-seconds/validation"] = epoch_time

        self._to_log["step"] = float(trainer.current_epoch)

        # Do not log during sanity check as results are not relevant
        if not trainer.sanity_checking:
            pl_module.log_dict(self._to_log)
            self._to_log = {}

    def on_validation_batch_end(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
        outputs: torch.Tensor,
        batch: typing.Mapping[str, typing.Any],
        batch_idx: int,
        dataloader_idx: int = 0,
    ) -> None:
        """Execute actions after a validation after ends (lightning callback).

        This method is executed whenever a validation batch ends.  Presumably,
        batches happen as often as possible.  You want to make this code very
        fast.  Do not log things to the terminal or the such, or do complicated
        (lengthy) calculations.

        .. warning::

           This is executed **while** you are training.  Be very succint or
           face the consequences of slow training!

        Parameters
        ----------
        trainer
            The Lightning trainer object.
        pl_module
            The lightning module that is being trained.
        outputs
            The outputs of the module's ``training_step``.
        batch
            The data that the training step received.
        batch_idx
            The relative number of the batch.
        dataloader_idx
            Index of the dataloader used during validation.  Use this to figure
            out which dataset was used for this validation epoch.
        """

        if dataloader_idx == 0:
            key = "loss/validation"
        else:
            key = f"loss/validation-{dataloader_idx}"

        batch_size = batch["image"].shape[0]

        pl_module.log(
            key,
            outputs.item(),
            prog_bar=False,
            on_step=False,
            on_epoch=True,
            batch_size=batch_size,
            add_dataloader_idx=False,
        )
