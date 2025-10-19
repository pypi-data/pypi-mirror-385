# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from datetime import datetime

import click
from clapper.click import ConfigCommand, verbosity_option

from .logging import setup_cli_logger
from .train import reusable_options as training_options

# avoids X11/graphical desktop requirement when creating plots
__import__("matplotlib").use("agg")

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

\b
  1. Train a lwnet model with drive dataset, on the CPU, for only two
     epochs, then runs prediction (inference) and evaluation on listed datasets,
     report performance as a table and figures:

     .. code:: sh

        $ mednet experiment -vv lwnet drive --epochs=2
""",
)
@training_options
@verbosity_option(logger=logger, expose_value=False)
@click.pass_context
def experiment(
    ctx,
    model,
    output_folder,
    epochs,
    batch_size,
    accumulate_grad_batches,
    drop_incomplete_batch,
    datamodule,
    validation_period,
    device,
    cache_samples,
    seed,
    parallel,
    monitoring_interval,
    augmentations,
    balance_classes,
    initial_weights,
    **_,
):  # numpydoc ignore=PR01
    """Run a complete experiment, from training, to prediction and evaluation.

    Accepts all of command-line options from the ``train`` script.

    This script is just a wrapper around the individual scripts for training,
    running prediction, and evaluating.  It organises the output in a preset way:

    .. code::

       └─ <output-folder>/  # the generated model will be here
          ├── predictions.json  # the prediction outputs
          └── evaluation.json  # the evaluation outputs

    Note that complete experiments do not have options related to specific task
    functionality. Only the most generic set of options is available. To
    execute specific tasks, use the specialized command-line interfaces
    available in task-specific command groups.
    """

    experiment_start_timestamp = datetime.now()

    train_start_timestamp = datetime.now()
    logger.info(f"Started training at {train_start_timestamp}")

    from .train import train

    ctx.invoke(
        train,
        model=model,
        output_folder=output_folder,
        epochs=epochs,
        batch_size=batch_size,
        accumulate_grad_batches=accumulate_grad_batches,
        drop_incomplete_batch=drop_incomplete_batch,
        datamodule=datamodule,
        validation_period=validation_period,
        device=device,
        cache_samples=cache_samples,
        seed=seed,
        parallel=parallel,
        monitoring_interval=monitoring_interval,
        augmentations=augmentations,
        balance_classes=balance_classes,
        initial_weights=initial_weights,
    )
    train_stop_timestamp = datetime.now()

    logger.info(f"Ended training in {train_stop_timestamp}")
    logger.info(f"Training runtime: {train_stop_timestamp-train_start_timestamp}")

    logger.info("Started train analysis")
    from .train_analysis import train_analysis

    logdir = output_folder / "logs"
    ctx.invoke(
        train_analysis,
        logdir=logdir,
        output_folder=output_folder,
    )

    logger.info("Ended train analysis")

    predict_start_timestamp = datetime.now()
    logger.info(f"Started prediction at {predict_start_timestamp}")

    from .predict import predict

    ctx.invoke(
        predict,
        output_folder=output_folder,
        model=model,
        datamodule=datamodule,
        batch_size=batch_size,
        device=device,
        weight=output_folder,
        parallel=parallel,
    )

    predict_stop_timestamp = datetime.now()
    logger.info(f"Ended prediction in {predict_stop_timestamp}")
    logger.info(f"Prediction runtime: {predict_stop_timestamp-predict_start_timestamp}")

    evaluation_start_timestamp = datetime.now()
    logger.info(f"Started evaluation at {evaluation_start_timestamp}")

    predictions_file = output_folder / "predictions.json"

    with (predictions_file).open() as pf:
        splits = json.load(pf).keys()

        if "validation" in splits:
            evaluation_threshold = "validation"
        elif "train" in splits:
            evaluation_threshold = "train"
        else:
            evaluation_threshold = None

    match datamodule.task:
        case "classification":
            from .classify.evaluate import evaluate

            ctx.invoke(
                evaluate,
                predictions=predictions_file,
                output_folder=output_folder,
                threshold=evaluation_threshold,
                plot=True,
            )

        case "segmentation":
            from .segment.evaluate import evaluate

            ctx.invoke(
                evaluate,
                predictions=predictions_file,
                output_folder=output_folder,
                threshold=evaluation_threshold,
                plot=True,
            )

        case "detection":
            from .detect.evaluate import evaluate

            ctx.invoke(
                evaluate,
                predictions=predictions_file,
                output_folder=output_folder,
            )

        case _:
            raise click.BadParameter(
                f"Do not know how to handle evaluation on `{datamodule.task}` "
                f"task from `{type(datamodule).__module__}.{type(datamodule).__name__}`"
            )

    evaluation_stop_timestamp = datetime.now()
    logger.info(f"Ended prediction in {evaluation_stop_timestamp}")
    logger.info(
        f"Prediction runtime: {evaluation_stop_timestamp-evaluation_start_timestamp}"
    )

    experiment_stop_timestamp = datetime.now()
    logger.info(
        f"Total experiment runtime: {experiment_stop_timestamp-experiment_start_timestamp}"
    )
