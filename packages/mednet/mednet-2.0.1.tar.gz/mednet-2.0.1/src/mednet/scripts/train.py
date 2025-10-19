# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import pathlib

import click
from clapper.click import ResourceOption, verbosity_option

from ..utils.string import rewrap
from .click import ConfigCommand, PathOrURL
from .logging import setup_cli_logger
from .utils import parse_checkpoint_metric

logger = setup_cli_logger()


def reusable_options(f):
    """Wrap reusable training script options (for ``experiment``).

    This decorator equips the target function ``f`` with all (reusable) ``train`` script
    options.

    Parameters
    ----------
    f
        The target function to equip with options.  This function must have parameters
        that accept such options.

    Returns
    -------
        The decorated version of function ``f``
    """

    @click.option(
        "--output-folder",
        "-o",
        help="Directory in which to store results (created if does not exist)",
        required=True,
        type=click.Path(
            file_okay=False,
            dir_okay=True,
            writable=True,
            path_type=pathlib.Path,
        ),
        default="results",
        show_default=True,
        cls=ResourceOption,
    )
    @click.option(
        "--model",
        "-m",
        help="A lightning module instance implementing the network to be trained",
        required=True,
        cls=ResourceOption,
    )
    @click.option(
        "--datamodule",
        "-d",
        help="A lightning DataModule containing the training and validation sets.",
        required=True,
        cls=ResourceOption,
    )
    @click.option(
        "--batch-size",
        "-b",
        help=rewrap(
            """Number of samples in every batch (this parameter affects memory
            requirements for the network).  If the number of samples in the batch is
            larger than the total number of samples available for training, this value
            is truncated.  If this number is smaller, then batches of the specified size
            are created and fed to the network until there are no more new samples to
            feed (epoch is finished). If the total number of training samples is not a
            multiple of the batch-size, the last batch will be smaller than the first,
            unless --drop-incomplete-batch is set, in which case this batch is not
            used."""
        ),
        required=True,
        show_default=True,
        default=1,
        type=click.IntRange(min=1),
        cls=ResourceOption,
    )
    @click.option(
        "--accumulate-grad-batches",
        "-a",
        help=rewrap(
            """Number of accumulations for backward propagation to accumulate "
            gradients over k batches before stepping the optimizer. This parameter, used
            in conjunction with the batch-size, may be used to reduce the number of
            samples loaded in each iteration, to affect memory usage in exchange for
            processing time (more iterations). This is useful interesting when one is
            training on GPUs with a limited amount of onboard RAM. The default of 1
            forces the whole batch to be processed at once. Otherwise the batch is
            multiplied by accumulate-grad-batches pieces, and gradients are accumulated
            to complete each training step."""
        ),
        required=True,
        show_default=True,
        default=1,
        type=click.IntRange(min=1),
        cls=ResourceOption,
    )
    @click.option(
        "--drop-incomplete-batch/--no-drop-incomplete-batch",
        "-D",
        help=rewrap(
            """If set, the last batch in an epoch will be dropped if incomplete. If you
            set this option, you should also consider increasing the total number of
            epochs of training, as the total number of training steps may be
            reduced."""
        ),
        required=True,
        show_default=True,
        default=False,
        cls=ResourceOption,
    )
    @click.option(
        "--epochs",
        "-e",
        help=rewrap(
            """Number of epochs (complete training set passes) to train for. If
            continuing from a saved checkpoint, ensure to provide a greater number of
            epochs than was saved in the checkpoint to be loaded."""
        ),
        show_default=True,
        required=True,
        default=1000,
        type=click.IntRange(min=1),
        cls=ResourceOption,
    )
    @click.option(
        "--validation-period",
        "-p",
        help=rewrap(
            """Number of epochs after which validation happens.  By default, we run
            validation after every training epoch (period=1).  You can change this to
            make validation more sparse, by increasing the validation period. Notice
            that this affects checkpoint saving.  While checkpoints are created after
            every training step (the last training step always triggers the overriding
            of latest checkpoint), and this process is independent of validation runs,
            evaluation of the 'best' model obtained so far based on those will be
            influenced by this setting."""
        ),
        show_default=True,
        required=True,
        default=1,
        type=click.IntRange(min=1),
        cls=ResourceOption,
    )
    @click.option(
        "--checkpoint-metric",
        "-c",
        help=rewrap(
            """
            Specifies the evaluation metric and optimization direction to monitor for saving
            the best checkpoint, in the format 'min/metric' or 'max/metric'. By default,
            this is set to 'min/loss'. You may change it to monitor a custom metric.
            The prefix 'min' indicates that the checkpoint with the lowest value of the
            given metric will be saved; 'max' means the checkpoint with the highest value
            will be saved. It is your responsibility to correctly log this metric at the end
            of each validation step under the name 'checkpoint-metric/validation', ideally
            using torchmetrics.
            """
        ),
        show_default=True,
        required=True,
        default="min/loss",
        type=parse_checkpoint_metric,
        cls=ResourceOption,
    )
    @click.option(
        "--device",
        "-x",
        help=rewrap(
            """A string indicating the device to use (e.g. "cpu", "cuda", "mps",
            "cuda:0"). Can be passed as a string, or as an environment variable (e.g.
            `MEDNET_DEVICE=cpu` or `MEDNET_DEVICE=mps`)."""
        ),
        envvar="MEDNET_DEVICE",
        show_default=True,
        required=True,
        default="cpu",
        cls=ResourceOption,
    )
    @click.option(
        "--cache-samples/--no-cache-samples",
        help="""If set to True, loads the sample into memory, otherwise loads them at
        runtime.""",
        required=True,
        show_default=True,
        default=False,
        cls=ResourceOption,
    )
    @click.option(
        "--seed",
        "-s",
        help="Seed to use for the random number generator",
        show_default=True,
        required=False,
        default=42,
        type=click.IntRange(min=0),
        cls=ResourceOption,
    )
    @click.option(
        "--parallel",
        "-P",
        help=rewrap(
            """Use multiprocessing for data loading: if set to -1 (default), disables
            multiprocessing data loading.  Set to 0 to enable as many data loading
            instances as processing cores available in the system.  Set to >= 1 to
            enable that many multiprocessing instances for data loading."""
        ),
        type=click.IntRange(min=-1),
        show_default=True,
        required=True,
        default=-1,
        cls=ResourceOption,
    )
    @click.option(
        "--monitoring-interval",
        "-I",
        help=rewrap(
            """Time between checks for the use of resources during each training epoch,
            in seconds.  An interval of 5 seconds, for example, will lead to CPU and GPU
            resources being probed every 5 seconds during each training epoch. Values
            registered in the training logs correspond to averages (or maxima) observed
            through possibly many probes in each epoch. Notice that setting a very small
            value may cause the probing process to become extremely busy, potentially
            biasing the overall perception of resource usage."""
        ),
        type=click.FloatRange(min=0.1),
        show_default=True,
        required=True,
        default=5.0,
        cls=ResourceOption,
    )
    @click.option(
        "--augmentations",
        "-A",
        help=rewrap(
            """Models that can be trained in this package are shipped without explicit
            data augmentations. This option allows you to define a list of data
            augmentations to use for training the selected model."""
        ),
        type=click.UNPROCESSED,
        default=[],
        cls=ResourceOption,
    )
    @click.option(
        "--balance-classes/--no-balance-classes",
        "-B/-N",
        help=rewrap(
            """If set, balances the loss term to take into consideration the occurence
            of each target in the training and validation splits."""
        ),
        required=True,
        show_default=True,
        default=True,
        cls=ResourceOption,
    )
    @click.option(
        "--initial-weights",
        "-W",
        help=rewrap(
            """Path or URL to pretrained model file (`.ckpt` extension), corresponding
            to the architecture set with `--model`. Optionally, you may also pass a
            directory containing the result of a training session, in which case either
            the best (lowest validation) or latest model will be loaded. Note these
            weights will be overwritten when re-starting training from a checkpoint.
            This parameter should only be used as a set of initial weights (when
            starting a new training session)."""
        ),
        required=False,
        cls=ResourceOption,
        type=PathOrURL(
            exists=True,
            file_okay=True,
            dir_okay=True,
            readable=True,
            path_type=pathlib.Path,
        ),
    )
    @functools.wraps(f)
    def wrapper_reusable_options(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper_reusable_options


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Train a Pasa model with the montgomery dataset (classification task):

   .. code:: sh

      mednet train -vv pasa montgomery

2. Train a Little WNet model with the drive dataset (vessel segmentation task):

   .. code:: sh

      mednet train -vv lwnet drive

3. Train a Densenet model with the shenzhen dataset, while starting from a set
   of pre-trained weights:

   .. code:: sh

      mednet train -vv densenet shenzhen --initial-weights=path/to/checkpoint.ckpt
""",
)
@reusable_options
@verbosity_option(logger=logger, expose_value=False)
def train(
    model,
    output_folder,
    epochs,
    batch_size,
    accumulate_grad_batches,
    drop_incomplete_batch,
    datamodule,
    validation_period,
    checkpoint_metric,
    device,
    cache_samples,
    seed,
    parallel,
    monitoring_interval,
    augmentations,
    balance_classes,
    initial_weights,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Train a model on a given datamodule (task-specific).

    Training is performed for a configurable number of epochs, and
    generates checkpoints.  Checkpoints are model files with a .ckpt
    extension that are used in subsequent tasks or from which training
    can be resumed.
    """
    from lightning.pytorch import seed_everything

    from ..engine.device import DeviceManager
    from ..engine.trainer import (
        get_checkpoint_file,
        load_checkpoint,
        run,
        setup_datamodule,
        validate_model_datamodule,
    )
    from ..models.model import Model
    from .utils import save_json_metadata

    validate_model_datamodule(model, datamodule)

    seed_everything(seed)

    # report model/transforms options - set data augmentations
    logger.info(f"Network model: {type(model).__module__}.{type(model).__name__}")
    model.augmentation_transforms = augmentations

    device_manager = DeviceManager(device)

    # reset datamodule with user configurable options
    setup_datamodule(
        datamodule, model, batch_size, drop_incomplete_batch, cache_samples, parallel
    )

    if initial_weights is not None:
        if isinstance(initial_weights, pathlib.Path):
            if initial_weights.is_dir():
                initial_weights = get_checkpoint_file(initial_weights)

        logger.info(f"Loading initial weights from `{initial_weights}`...")
        model = type(model).load_from_checkpoint(initial_weights, strict=False)

    # resets the number of outputs in a model, if necessary
    model.num_classes = datamodule.num_classes

    # If asked, rebalances the loss criterion based on the relative proportion
    # of class examples available in the training set.  Also affects the
    # validation loss if a validation set is available on the DataModule.
    if balance_classes:
        model.balance_losses(datamodule)

    checkpoint_file = get_checkpoint_file(output_folder)

    if checkpoint_file is None:
        if isinstance(model, Model):
            if not model.normalizer_is_set():
                model.set_normalizer_from_dataloader(
                    datamodule.unshuffled_train_dataloader()
                )
        else:
            from ..utils.string import rewrap

            logger.warning(
                rewrap(
                    f"""Model `{type(model)}` is not known. Skipping input normalization
                    from train dataloader setup (unsupported external model)."""
                ),
            )
    else:
        load_checkpoint(checkpoint_file)

    ckpt_metric, ckpt_mode = checkpoint_metric
    # stores all information we can think of, to reproduce this later
    save_json_metadata(
        output_file=output_folder / "train.meta.json",
        datamodule=datamodule,
        model=model,
        augmentations=augmentations,
        device_manager=device_manager,
        output_folder=output_folder,
        epochs=epochs,
        batch_size=batch_size,
        accumulate_grad_batches=accumulate_grad_batches,
        drop_incomplete_batch=drop_incomplete_batch,
        validation_period=validation_period,
        checkpoint_metric=ckpt_metric,
        checkpoint_mode=ckpt_mode,
        cache_samples=cache_samples,
        seed=seed,
        parallel=parallel,
        monitoring_interval=monitoring_interval,
        balance_classes=balance_classes,
        initial_weights=initial_weights,
    )

    logger.info(f"Training for at most {epochs} epochs.")

    run(
        model=model,
        datamodule=datamodule,
        validation_period=validation_period,
        checkpoint_metric=ckpt_metric,
        checkpoint_mode=ckpt_mode,
        device_manager=device_manager,
        max_epochs=epochs,
        output_folder=output_folder,
        monitoring_interval=monitoring_interval,
        accumulate_grad_batches=accumulate_grad_batches,
        checkpoint=checkpoint_file,
    )
