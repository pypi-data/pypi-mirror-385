# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import warnings

import clapper.click
import click

from ..utils.string import rewrap
from .click import ConfigCommand, PathOrURL
from .logging import setup_cli_logger

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Run prediction on an existing DataModule configuration:

   .. code:: sh

      mednet predict -vv lwnet drive --weight=path/to/model.ckpt --output-folder=path/to/predictions

2. Enable multi-processing data loading with 6 processes:

   .. code:: sh

      mednet predict -vv lwnet drive --parallel=6 --weight=path/to/model.ckpt --output-folder=path/to/predictions

""",
)
@click.option(
    "--output-folder",
    "-o",
    help="Directory in which to save predictions (created if does not exist)",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    default="results",
    show_default=True,
    cls=clapper.click.ResourceOption,
)
@click.option(
    "--model",
    "-m",
    help="""A lightning module instance implementing the network architecture
    (not the weights, necessarily) to be used for prediction.""",
    required=True,
    cls=clapper.click.ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help=rewrap(
        """A lightning DataModule that will be asked for prediction data loaders.
            Typically, this includes all configured splits in a DataModule, however this
            is not a requirement.  A DataModule that returns a single dataloader for
            prediction (wrapped in a dictionary) is acceptable."""
    ),
    required=True,
    cls=clapper.click.ResourceOption,
)
@click.option(
    "--batch-size",
    "-b",
    help=rewrap(
        """Number of samples in every batch (this parameter affects memory requirements
        for the network)."""
    ),
    required=True,
    show_default=True,
    default=1,
    type=click.IntRange(min=1),
    cls=clapper.click.ResourceOption,
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
    cls=clapper.click.ResourceOption,
)
@click.option(
    "--weight",
    "-w",
    help=rewrap(
        """Path or URL to pretrained model file (`.ckpt` extension), corresponding to
        the architecture set with `--model`.  Optionally, you may also pass a directory
        containing the result of a training session, in which case either the best
        (lowest validation) or latest model will be loaded."""
    ),
    required=True,
    cls=clapper.click.ResourceOption,
    type=PathOrURL(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--parallel",
    "-P",
    help=rewrap(
        """Use multiprocessing for data loading: if set to -1 (default), disables
        multiprocessing data loading.  Set to 0 to enable as many data loading instances
        as processing cores available in the system.  Set to >= 1 to enable that many
        multiprocessing instances for data loading."""
    ),
    type=click.IntRange(min=-1),
    show_default=True,
    required=True,
    default=-1,
    cls=clapper.click.ResourceOption,
)
@clapper.click.verbosity_option(logger=logger, expose_value=False)
def predict(
    output_folder,
    model,
    datamodule,
    batch_size,
    device,
    weight,
    parallel,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Run inference on input samples, using a pre-trained model."""

    from ..engine.device import DeviceManager
    from ..engine.trainer import validate_model_datamodule
    from ..utils.checkpointer import get_checkpoint_to_run_inference
    from .utils import (
        JSONable,
        get_ckpt_metric_mode,
        save_json_metadata,
        save_json_with_backup,
    )

    validate_model_datamodule(model, datamodule)

    # sets-up the data module
    datamodule.batch_size = batch_size
    datamodule.parallel = parallel
    datamodule.model_transforms = list(model.model_transforms)

    datamodule.prepare_data()
    datamodule.setup(stage="predict")

    if isinstance(weight, pathlib.Path) and weight.is_dir():
        metric, mode = get_ckpt_metric_mode(output_folder / "train.meta.json")
        weight = get_checkpoint_to_run_inference(path=weight, metric=metric, mode=mode)

    logger.info(f"Loading checkpoint from `{weight}`...")
    if hasattr(model, "peft_config") and model.peft_config is not None:
        # When using PEFT methods, checkpoint loading is handled by the PEFT library,
        # which relies on its own checkpoint format. This often leads to warnings
        # about key mismatches between the checkpoint and the model's state_dict.
        # To avoid cluttering the output with these expected messages, those specific
        # warnings are being suppressed in the block below.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Found keys that are*")
            model = type(model).load_from_checkpoint(weight, strict=False)
    else:
        model = type(model).load_from_checkpoint(weight, strict=False)

    device_manager = DeviceManager(device)

    save_json_metadata(
        output_file=output_folder / "predictions.meta.json",
        output_folder=output_folder,
        model=model,
        datamodule=datamodule,
        batch_size=batch_size,
        device=device,
        weight=weight,
        parallel=parallel,
    )

    predictions: JSONable = None
    match datamodule.task:
        case "classification":
            from ..engine.classify.predictor import run as run_classify

            logger.info(f"Running prediction for `{datamodule.task}` task...")
            predictions = run_classify(model, datamodule, device_manager)

        case "segmentation":
            from ..engine.segment.predictor import run as run_segment

            logger.info(f"Running prediction for `{datamodule.task}` task...")
            predictions = run_segment(model, datamodule, device_manager, output_folder)

        case "detection":
            from ..engine.detect.predictor import run as run_detect

            logger.info(f"Running prediction for `{datamodule.task}` task...")
            predictions = run_detect(model, datamodule, device_manager)

        case _:
            raise click.BadParameter(
                f"Do not know how to handle `{datamodule.task}` task from "
                f"`{type(datamodule).__module__}.{type(datamodule).__name__}`"
            )

    predictions_file = output_folder / "predictions.json"
    save_json_with_backup(predictions_file, predictions)
    logger.info(f"Predictions saved to `{str(predictions_file)}`")
