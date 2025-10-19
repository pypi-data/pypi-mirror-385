# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import click
from clapper.click import ResourceOption, verbosity_option

from .click import ConfigCommand
from .logging import setup_cli_logger

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Upload an existing experiment result from a path it resides on (with a default experiment name as {model-name}_{database-name} and a default run name as {date-time}):

   .. code:: sh

      mednet upload --experiment-folder=/path/to/results

2. Upload an existing experiment result with an experiment name:

   .. code:: sh

      mednet upload --experiment-folder=/path/to/results --experiment-name=exp-pasa_mc

3. Upload an existing experiment result with a run name:

   .. code:: sh

      mednet upload --experiment-folder=/path/to/results --run-name=run-1

4. Upload an existing experiment result with defining a size limit of 20MB for each file:

   .. code:: sh

      mednet upload --experiment-folder=/path/to/results --upload-limit-mb=20

""",
)
@click.option(
    "--project-path",
    "-p",
    help="Path to the project where to upload model entries",
    required=True,
    type=str,
    default="medai/software/mednet",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--experiment-folder",
    "-e",
    help="Directory in which to upload results from",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        path_type=pathlib.Path,
    ),
    default="results",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--experiment-name",
    "-n",
    help='A string indicating the experiment name (e.g. "exp-pasa-mc" or "exp-densenet-mc-ch")',
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--run-name",
    "-r",
    help='A string indicating the run name (e.g. "run-1")',
    required=True,
    default="",
    cls=ResourceOption,
)
@click.option(
    "--upload-limit-mb",
    "-l",
    help="Maximim upload size in MB (set to 0 for no limit).",
    show_default=True,
    required=True,
    default=10,
    type=click.IntRange(min=0),
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def upload(
    project_path: str,
    experiment_folder: pathlib.Path,
    experiment_name: str,
    run_name: str,
    upload_limit_mb: int,
    **_,  # ignored
) -> None:  # numpydoc ignore=PR01
    """Upload results from a classification experiment folder to GitLab's MLFlow server."""

    from ..engine.uploader import run

    # further metrics to be displayed
    metrics = [
        "threshold",
        "precision",
        "recall",
        "f1",
        "average_precision",
        "specificity",
        "roc_auc",
        "accuracy",
    ]

    run(
        project_path=project_path,
        experiment_folder=experiment_folder,
        experiment_name=experiment_name,
        run_name=run_name,
        metrics=metrics,
        upload_limit_mb=upload_limit_mb,
    )
