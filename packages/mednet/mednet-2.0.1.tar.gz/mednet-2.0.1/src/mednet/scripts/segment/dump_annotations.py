# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import clapper.click
import clapper.logging
import click

from ..click import ConfigCommand

logger = clapper.logging.setup(
    __name__.split(".")[0], format="%(levelname)s: %(message)s"
)


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Dump annotations for a dataset after pre-processing on a particular directory:

   .. code:: sh

      mednet segment dump-annotations -vv lwnet drive-2nd --output-folder=path/to/annotations

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
    default="predictions",
    show_default=True,
    cls=clapper.click.ResourceOption,
)
@click.option(
    "--model",
    "-m",
    help="""A lightning module instance that will be used to retrieve
    pre-processing transforms.""",
    required=True,
    cls=clapper.click.ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help="""A lightning DataModule that will be asked for prediction data
    loaders. Typically, this includes all configured splits in a DataModule,
    however this is not a requirement.  A DataModule that returns a single
    dataloader for prediction (wrapped in a dictionary) is acceptable.""",
    required=True,
    cls=clapper.click.ResourceOption,
)
@clapper.click.verbosity_option(logger=logger, expose_value=False)
def dump_annotations(
    output_folder, model, datamodule, **_
) -> None:  # numpydoc ignore=PR01
    """Dump annotations in a given folder, after pre-processing."""

    from ...engine.segment.dumper import run
    from ...engine.trainer import validate_model_datamodule
    from ..utils import save_json_metadata, save_json_with_backup

    validate_model_datamodule(model, datamodule)
    assert datamodule.task == "segmentation"

    # sets-up the data module
    datamodule.model_transforms = list(model.model_transforms)
    datamodule.batch_size = 1
    datamodule.parallel = -1
    datamodule.prepare_data()
    datamodule.setup(stage="predict")

    # stores all information we can think of, to reproduce this later
    save_json_metadata(
        output_file=output_folder / "annotations.meta.json",
        output_folder=output_folder,
        model=model,
        datamodule=datamodule,
    )

    json_data = run(datamodule, output_folder)

    base_file = output_folder / "annotations.json"
    save_json_with_backup(base_file, json_data)
    logger.info(f"Annotations saved to `{str(base_file)}`")
