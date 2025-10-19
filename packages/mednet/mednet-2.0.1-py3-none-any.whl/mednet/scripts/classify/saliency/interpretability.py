# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import click
from clapper.click import ResourceOption, verbosity_option

from ...click import ConfigCommand
from ...logging import setup_cli_logger

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Evaluate the generated saliency maps for their localization performance:

   .. code:: sh

      mednet classify saliency interpretability -vv pasa tbx11k-v1-healthy-vs-atb --input-folder=parent-folder/saliencies/ --output-json=path/to/interpretability-scores.json

""",
)
@click.option(
    "--model",
    "-m",
    help="""A lightning module instance implementing the network architecture
    (not the weights, necessarily) to be used for inference.  Currently, only
    supports pasa and densenet models.""",
    required=True,
    type=click.UNPROCESSED,
    cls=ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help="""A lightning DataModule that will be asked for prediction data
    loaders. Typically, this includes all configured splits in a DataModule,
    however this is not a requirement.  A DataModule that returns a single
    dataloader for prediction (wrapped in a dictionary) is acceptable.""",
    required=True,
    type=click.UNPROCESSED,
    cls=ResourceOption,
)
@click.option(
    "--input-folder",
    "-i",
    help="""Path from where to load saliency maps.  You can generate saliency
    maps with ``mednet classify saliency generate``.""",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=pathlib.Path,
    ),
    default="saliency-maps",
    cls=ResourceOption,
)
@click.option(
    "--target-label",
    "-t",
    help="""The target label that will be analysed.  It must match the target
    label that was used to generate the saliency maps provided with option
    ``--input-folder``.  Samples with all other labels are ignored.""",
    required=True,
    type=click.INT,
    default=1,
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--output-folder",
    "-o",
    help="""Path to the folder in which all measures will be saved.""",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        path_type=pathlib.Path,
        writable=True,
    ),
    default="results",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--only-dataset",
    "-S",
    help="""If set, will only run the command for the named dataset on the
    provided datamodule, skipping any other dataset.""",
    cls=ResourceOption,
)
@click.option(
    "--plot/--no-plot",
    "-P",
    help="""If set, then also produces figures containing the plots of
    score histograms.""",
    required=True,
    show_default=True,
    default=True,
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def interpretability(
    model,
    datamodule,
    input_folder,
    target_label,
    output_folder,
    only_dataset,
    plot: bool,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Evaluate saliency map agreement with annotations (human
    interpretability).

    The evaluation happens by comparing saliency maps with ground-truth
    provided by any other means (typically following a manual annotation
    procedure).

    .. note::

       For obvious reasons, this evaluation is limited to datasets that
       contain built-in annotations which corroborate classification.

    As a result of the evaluation, this application creates a single .json file
    that resembles the original DataModule, with added information containing
    the following measures, for each sample:

    * Proportional Energy: A measure that compares (UNthresholed) saliency maps
      with annotations (based on :cite:p:`wang_score-cam_2020`). It estimates how much
      activation lies within the ground truth boxes compared to the total sum
      of the activations.

    * Average Saliency Focus: estimates how much of the ground truth bounding
      boxes area is covered by the activations.  It is similar to the
      proportional energy measure in the sense that it does not need explicit
      thresholding.
    """

    import matplotlib.backends.backend_pdf

    from ....engine.classify.saliency.interpretability import run
    from ....engine.classify.saliency.utils import make_plots, make_table
    from ....scripts.utils import save_json_metadata, save_json_with_backup

    datamodule.model_transforms = list(model.model_transforms)
    datamodule.batch_size = 1
    datamodule.prepare_data()
    datamodule.setup(stage="predict")

    output_json = output_folder / "interpretability.json"

    # stores all information we can think of, to reproduce this later
    save_json_metadata(
        output_file=output_json.with_suffix(".meta.json"),
        model=model,
        datamodule=datamodule,
        output_json=output_json,
        input_folder=input_folder,
        target_label=target_label,
        only_dataset=only_dataset,
        plot=plot,
    )

    results = run(
        input_folder=input_folder,
        target_label=target_label,
        datamodule=datamodule,
        only_dataset=only_dataset,
    )

    logger.info(f"Saving output file to `{str(output_json)}`...")
    save_json_with_backup(output_json, results)

    table = make_table(
        results=results, indexes={2: "PropEng", 3: "AvgSalFocus"}, format_="rst"
    )
    output_table = output_json.with_suffix(".rst")
    logger.info(f"Saving output summary table to `{str(output_table)}`...")
    with output_table.open("w") as f:
        f.write(table)
    click.echo(table)

    # Plots histograms, if the user asked to do so.
    if plot:
        figure_path = output_json.with_suffix(".pdf")
        logger.info(f"Saving plots to `{str(figure_path)}`...")
        with matplotlib.backends.backend_pdf.PdfPages(figure_path) as pdf:
            for fig in make_plots(
                results=results,
                indexes={2: "Proportional Energy", 3: "Average Saliency Focus"},
            ):
                pdf.savefig(fig)
