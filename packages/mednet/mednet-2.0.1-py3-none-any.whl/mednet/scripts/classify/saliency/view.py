# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import click
from clapper.click import ConfigCommand, ResourceOption, verbosity_option

from ...logging import setup_cli_logger

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Generate visualizations in the form of heatmaps from existing saliency maps for a dataset configuration:

   .. code:: sh

      mednet classify saliency view -vv pasa tbx11k-v1-healthy-vs-atb --input-folder=parent_folder/gradcam/ --output-folder=path/to/visualizations
""",
)
@click.option(
    "--model",
    "-m",
    help="A lightning module instance implementing the network to be used for applying the necessary data transformations.",
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help="A lightning DataModule containing the training, validation and test sets.",
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--input-folder",
    "-i",
    help="Path to the directory containing the saliency maps for a specific visualization type.",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    default="visualizations",
    cls=ResourceOption,
)
@click.option(
    "--output-folder",
    "-o",
    help="Directory in which to store the visualizations (created if does not exist)",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    default="visualizations",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--show-groundtruth/--no-show-groundtruth",
    "-G/-g",
    help="""If set, visualizations for ground truth labels will be generated.
    Only works for datasets with bounding boxes.""",
    is_flag=True,
    default=False,
    cls=ResourceOption,
)
@click.option(
    "--threshold",
    "-t",
    help="""The pixel values above ``threshold`` % of max value are kept in the
    original saliency map.  Everything else is set to zero.  The value proposed
    on :cite:p:`wang_score-cam_2020` is 0.2.  Use this value if unsure.""",
    show_default=True,
    required=True,
    default=0.2,
    type=click.FloatRange(min=0, max=1),
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def view(
    model,
    datamodule,
    input_folder,
    output_folder,
    show_groundtruth,
    threshold,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Generate heatmaps for input samples based on existing saliency maps."""

    from ....engine.classify.saliency.viewer import run
    from ...utils import save_json_metadata

    logger.info(f"Output folder: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    # register metadata
    save_json_metadata(
        output_file=output_folder / "view.meta.json",
        datamodule=datamodule,
        model=model,
        input_folder=input_folder,
        output_folder=output_folder,
        show_groundtruth=show_groundtruth,
        threshold=threshold,
    )

    datamodule.drop_incomplete_batch = False
    # datamodule.cache_samples = cache_samples
    # datamodule.parallel = parallel
    datamodule.model_transforms = model.model_transforms

    datamodule.prepare_data()
    datamodule.setup(stage="predict")

    run(
        datamodule=datamodule,
        input_folder=input_folder,
        target_label=1,
        output_folder=output_folder,
        show_groundtruth=show_groundtruth,
        threshold=threshold,
    )
