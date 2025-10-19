# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import typing

import click
from clapper.click import ResourceOption, verbosity_option

from ...engine.segment.evaluator import SUPPORTED_METRIC_TYPE
from ..click import ConfigCommand
from ..logging import setup_cli_logger

# avoids X11/graphical desktop requirement when creating plots
__import__("matplotlib").use("agg")

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

\b
  1. Runs evaluation from existing predictions:

     .. code:: sh

        $ mednet segment evaluate -vv --predictions=path/to/predictions.json --output-folder=path/to/results

  2. Runs evaluation from existing predictions, incorporate a second set of
     annotations into the evaluation:

     .. code:: sh

        $ mednet segment evaluate -vv --predictions=path/to/predictions.json --compare-annotator=path/to/annotations.json --output-folder=path/to/results
""",
)
@click.option(
    "--predictions",
    "-p",
    help="""Path to the JSON file describing available predictions. The actual
    predictions are supposed to lie on the same folder.""",
    required=True,
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=False,
        path_type=pathlib.Path,
    ),
    cls=ResourceOption,
)
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
    "--threshold",
    "-t",
    help="""This number is used to define positives and negatives from
    probability maps, and used to report metrics based on a threshold chosen *a
    priori*. It can be set to a floating-point value, or to the name of dataset
    split in ``--predictions``.
    """,
    default="0.5",
    show_default=True,
    required=False,
    cls=ResourceOption,
)
@click.option(
    "--metric",
    "-m",
    help="""If threshold is set to the name of a split in ``--predictions``,
    then this parameter defines the metric function to be used to evaluate the
    threshold at which the metric reaches its maximum value. All other splits
    are evaluated with respect to this threshold.""",
    default="f1",
    type=click.Choice(typing.get_args(SUPPORTED_METRIC_TYPE), case_sensitive=True),
    show_default=True,
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--steps",
    "-s",
    help="""Number of steps for evaluating metrics on various splits. This
    value is used when drawing precision-recall plots, or when deciding the
    highest metric value on splits.""",
    default=100,
    type=click.IntRange(10),
    show_default=True,
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--compare-annotator",
    "-a",
    help="""Path to a JSON file as produced by the CLI ``dump-annotations``,
    containing splits and sample lists with associated HDF5 files where we can
    find pre-processed annotation masks.  These annotations will be compared
    with the target annotations on the main predictions.  In this case, a row
    is added for each available split in the evaluation table.""",
    required=False,
    default=None,
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=False,
        path_type=pathlib.Path,
    ),
    cls=ResourceOption,
)
@click.option(
    "--plot/--no-plot",
    "-P",
    help="""If set, then also produces figures containing the plots of
    performance curves and score histograms.""",
    required=True,
    show_default=True,
    default=True,
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def evaluate(
    predictions: pathlib.Path,
    output_folder: pathlib.Path,
    threshold: str | float,
    metric: SUPPORTED_METRIC_TYPE,
    steps: int,
    compare_annotator: pathlib.Path,
    plot: bool,
    **_,  # ignored
):  # numpydoc ignore=PR01
    """Evaluate predictions (from a model) on a segmentation task."""

    import matplotlib.backends.backend_pdf

    from ...engine.segment.evaluator import (
        compare_annotators,
        make_plots,
        make_table,
        run,
    )
    from ..utils import save_json_metadata, save_json_with_backup

    evaluation_file = output_folder / "evaluation.json"

    save_json_metadata(
        output_file=evaluation_file.with_suffix(".meta.json"),
        predictions=str(predictions),
        output_folder=str(output_folder),
        threshold=threshold,
        metric=metric,
        steps=steps,
        compare_annotator=str(compare_annotator),
        plot=plot,
    )

    eval_json_data, threshold_value = run(predictions, steps, threshold, metric)

    if compare_annotator is not None:
        logger.info(f"Comparing 2nd. annotator using `{str(compare_annotator)}`...")
        comparison = compare_annotators(predictions, compare_annotator)
        assert comparison, (
            f"No matching split-names found on `{str(compare_annotator)}`. "
            f"Are these the right annotations?"
        )
        for split_name, values in comparison.items():
            eval_json_data.setdefault(split_name, {})["second_annotator"] = values

    # Records full result analysis to a JSON file
    logger.info(f"Saving evaluation results at `{str(evaluation_file)}`...")
    save_json_with_backup(evaluation_file, eval_json_data)

    # Produces and records table
    table = make_table(eval_json_data, threshold_value, "rst")
    click.echo(table)

    output_table = evaluation_file.with_suffix(".rst")
    logger.info(f"Saving tabulated performance summary at `{str(output_table)}`...")
    output_table.parent.mkdir(parents=True, exist_ok=True)
    with output_table.open("w") as f:
        f.write(table)

    # Plots pre-calculated curves, if the user asked to do so.
    if plot:
        figure_path = evaluation_file.with_suffix(".pdf")
        logger.info(f"Saving evaluation figures at `{str(figure_path)}`...")
        with matplotlib.backends.backend_pdf.PdfPages(figure_path) as pdf:
            for fig in make_plots(eval_json_data):
                pdf.savefig(fig)
