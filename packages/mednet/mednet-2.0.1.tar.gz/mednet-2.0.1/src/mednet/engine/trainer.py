# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Functions supporting training of pytorch models."""

import logging
import os
import pathlib
import typing

import lightning.pytorch
import lightning.pytorch.callbacks
import torch

from ..data.datamodule import ConcatDataModule
from ..models.model import Model
from ..utils.checkpointer import CHECKPOINT_ALIASES
from ..utils.resources import ResourceMonitor
from .callbacks import LoggingCallback
from .device import DeviceManager

logger = logging.getLogger(__name__)


def get_checkpoint_file(results_dir: pathlib.Path) -> pathlib.Path | None:
    """Return the path of the latest checkpoint if it exists.

    Parameters
    ----------
    results_dir
        Directory in which results are saved.

    Returns
    -------
        Path to the latest checkpoint
    """
    from ..utils.checkpointer import get_checkpoint_to_resume_training

    checkpoint_file = None
    if results_dir.is_dir():
        try:
            checkpoint_file = get_checkpoint_to_resume_training(results_dir)
        except FileNotFoundError:
            logger.info(
                f"Folder {results_dir} already exists, but I did not"
                f" find any usable checkpoint file to resume training"
                f" from. Starting from scratch...",
            )

    return checkpoint_file


def load_checkpoint(checkpoint_file: pathlib.Path):
    """Load the checkpoint.

    Parameters
    ----------
    checkpoint_file
        Path to the checkpoint.
    """

    # Normalizer will be loaded during model.on_load_checkpoint
    checkpoint = torch.load(checkpoint_file, weights_only=False)
    start_epoch = checkpoint["epoch"]
    logger.info(
        f"Resuming from epoch {start_epoch} "
        f"(checkpoint file: `{str(checkpoint_file)}`)...",
    )


def setup_datamodule(
    datamodule: ConcatDataModule,
    model: Model,
    batch_size: int,
    drop_incomplete_batch: bool,
    cache_samples: bool,
    parallel: int,
) -> None:  # numpydoc ignore=PR01
    """Configure and set up the datamodule."""
    datamodule.batch_size = batch_size
    datamodule.drop_incomplete_batch = drop_incomplete_batch
    datamodule.cache_samples = cache_samples
    datamodule.parallel = parallel
    datamodule.model_transforms = model.model_transforms

    datamodule.prepare_data()
    datamodule.setup(stage="fit")


def validate_model_datamodule(model: Model, datamodule: ConcatDataModule):
    """Validate the use of a model and datamodule together.

    Parameters
    ----------
    model
        The model to be validated.
    datamodule
        The datamodule to be validated.

    Raises
    ------
    TypeError
        In case the types of both objects is not compatible.
    """

    from ..models.classify.model import Model as ClassificationModel
    from ..models.detect.model import Model as DetectionModel
    from ..models.segment.model import Model as SegmentationModel

    # asserts data module and model are compatible
    match model:
        case ClassificationModel():
            if datamodule.task != "classification":
                raise TypeError(
                    f"Classification model `{model.name}` is incompatible with "
                    f"`{datamodule.task}` task from datamodule "
                    f"`{datamodule.database_name}`."
                )
        case SegmentationModel():
            if datamodule.task != "segmentation":
                raise TypeError(
                    f"Segmentation model `{model.name}` is incompatible with "
                    f"`{datamodule.task}` task from datamodule "
                    f"`{datamodule.database_name}`."
                )
        case DetectionModel():
            if datamodule.task != "detection":
                raise TypeError(
                    f"Detection model `{model.name}` is incompatible with "
                    f"`{datamodule.task}` task from datamodule "
                    f"`{datamodule.database_name}`."
                )
        case _:
            raise TypeError(f"Do not know how to handle model of type `{type(model)}`")


def run(
    model: lightning.pytorch.LightningModule,
    datamodule: lightning.pytorch.LightningDataModule,
    validation_period: int,
    checkpoint_metric: str,
    checkpoint_mode: typing.Literal["min", "max"],
    device_manager: DeviceManager,
    max_epochs: int,
    output_folder: pathlib.Path,
    monitoring_interval: int | float,
    accumulate_grad_batches: int,
    checkpoint: pathlib.Path | None,
):
    """Fit a CNN model using supervised learning and save it to disk.

    This method supports periodic checkpointing and the output of a
    tensorboard-formatted log with the evolution of some figures during training.

    Parameters
    ----------
    model
        Neural network model (e.g. pasa).
    datamodule
        The lightning DataModule to use for training **and** validation.
    validation_period
        Number of epochs after which validation happens.  By default, we run
        validation after every training epoch (period=1).  You can change this
        to make validation more sparse, by increasing the validation period.
        Notice that this affects checkpoint saving.  While checkpoints are
        created after every training step (the last training step always
        triggers the overriding of latest checkpoint), and that this process is
        independent of validation runs, evaluation of the 'best' model obtained
        so far based on those will be influenced by this setting.
    checkpoint_metric
        Name of the metric to monitor for saving the best checkpoint. By default,
        the chosen metric is the loss associated to the model. You can change this
        to use a custom metric. It is your responsibility to log it correctly in the
        model (as 'checkpoint-metric/validation') at the end of each validation step,
        ideally using torchmetrics.
    checkpoint_mode
        It defines the optimization direction for saving the best checkpoint based
        on the selected evaluation metric. 'min' to save the checkpoint with the lowest
        value of the monitored metric. 'max' to save the checkpoint with the highest
        value of the monitored metric.
    device_manager
        An internal device representation, to be used for training and
        validation.  This representation can be converted into a pytorch device
        or a lightning accelerator setup.
    max_epochs
        The maximum number of epochs to train for.
    output_folder
        Folder in which the results will be saved.
    monitoring_interval
        Interval, in seconds (or fractions), through which we should monitor
        resources during training.
    accumulate_grad_batches
        Number of accumulations for backward propagation to accumulate gradients
        over k batches before stepping the optimizer. The default of 1 forces
        the whole batch to be processed at once. Otherwise the batch is multiplied
        by accumulate-grad-batches pieces, and gradients are accumulated to complete
        each step. This is especially interesting when one is training on GPUs with
        a limited amount of onboard RAM.
    checkpoint
        Path to an optional checkpoint file to load.
    """

    output_folder.mkdir(parents=True, exist_ok=True)

    from .loggers import CustomTensorboardLogger

    log_dir = "logs"
    tensorboard_logger = CustomTensorboardLogger(
        output_folder,
        log_dir,
    )
    logger.info(
        f"Monitor training with `tensorboard serve "
        f"--logdir={output_folder}/{log_dir}/`. "
        f"Then, open a browser on the printed address.",
    )

    resource_monitor = ResourceMonitor(
        interval=monitoring_interval,
        device_type=device_manager.device_type,
        main_pid=os.getpid(),
    )

    # This checkpointer will operate at the end of every validation epoch
    # (which happens at each checkpoint period), it will then save the lowest
    # validation loss model observed.  It will also save the last trained model
    checkpoint_minvalloss_callback = lightning.pytorch.callbacks.ModelCheckpoint(
        dirpath=output_folder,
        filename=CHECKPOINT_ALIASES["best"](checkpoint_metric, checkpoint_mode),  # type: ignore
        save_last=True,  # will (re)create the last trained model, at every iteration
        monitor=f"{checkpoint_metric}/validation",
        mode=checkpoint_mode,
        save_on_train_epoch_end=True,
        every_n_epochs=validation_period,  # frequency at which it checks the "monitor"
        enable_version_counter=False,  # no versioning of aliased checkpoints
    )
    checkpoint_minvalloss_callback.CHECKPOINT_NAME_LAST = CHECKPOINT_ALIASES[  # type: ignore
        "periodic"
    ]

    # This context guarantees that the start/stop of the monitoring thread will work
    # irrespectively of exceptions thrown by the code
    with resource_monitor:
        accelerator, devices = device_manager.lightning_accelerator()
        trainer = lightning.pytorch.Trainer(
            accelerator=accelerator,
            devices=devices,
            max_epochs=max_epochs,
            accumulate_grad_batches=accumulate_grad_batches,
            logger=tensorboard_logger,
            check_val_every_n_epoch=validation_period,
            log_every_n_steps=len(datamodule.train_dataloader()),
            callbacks=[
                LoggingCallback(resource_monitor),
                checkpoint_minvalloss_callback,
            ],
        )

        checkpoint_str = checkpoint if checkpoint is None else str(checkpoint)
        _ = trainer.fit(model, datamodule, ckpt_path=checkpoint_str)
