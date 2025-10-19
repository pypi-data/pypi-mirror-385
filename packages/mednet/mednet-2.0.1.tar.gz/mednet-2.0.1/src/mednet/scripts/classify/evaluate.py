# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import click
from clapper.click import ResourceOption, verbosity_option

from ..click import ConfigCommand
from ..logging import setup_cli_logger

# avoids X11/graphical desktop requirement when creating plots
__import__("matplotlib").use("agg")

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Run evaluation on an existing prediction output:

   .. code:: sh

      mednet classify evaluate -vv --predictions=path/to/predictions.json

2. Run evaluation on an existing prediction output, tune threshold a priori on the `validation` set:

   .. code:: sh

      mednet classify evaluate -vv --predictions=path/to/predictions.json --threshold=validation
""",
)
@click.option(
    "--predictions",
    "-p",
    help="Filename in which predictions are currently stored",
    required=True,
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=True,
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
    help="""This value is used to define positives and negatives from
    probability outputs in predictions, and report performance measures on
    **binary** classification tasks. It should either come from the training
    set or a separate validation set to avoid biasing the analysis.
    Optionally, if you provide a multi-split set of predictions as input, this
    may also be the name of an existing split (e.g. ``validation``) from which
    the threshold will be estimated (by calculating the threshold leading to
    the highest F1-score on that set) and then applied to the subsequent
    sets.  This value is not used for multi-class classification tasks.""",
    default=0.5,
    show_default=True,
    required=True,
    type=click.STRING,
    cls=ResourceOption,
)
@click.option(
    "--binning",
    "-b",
    help="""The binning algorithm to use for computing the bin widths and
    distribution for histograms.  Choose from algorithms supported by
    :py:func:`numpy.histogram`, or a simple integer indicating the number of
    bins to have in the interval ``[0, 1]``.""",
    default="50",
    show_default=True,
    required=True,
    type=click.STRING,
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
@click.option(
    "--credible-regions/--no-credible-regions",
    "-I",
    help="""If set, then evaluates also credible intervals. Notice the
        evaluation of ROC-AUC and Average Precision confidence margins can be
        rather slow for larger datasets.""",
    required=True,
    show_default=True,
    default=False,
    cls=ResourceOption,
)
@click.option(
    "--seed",
    "-s",
    help="""Seed to use for the random number generator (used when doing Monte Carlo "
    simulations required for the evaluation of credible regions for F1-score).""",
    show_default=True,
    required=False,
    default=42,
    type=click.IntRange(min=0),
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def evaluate(
    predictions: pathlib.Path,
    output_folder: pathlib.Path,
    threshold: str | float,
    binning: str,
    plot: bool,
    credible_regions: bool,
    seed: int,
    **_,  # ignored
) -> None:  # numpydoc ignore=PR01
    """Evaluate predictions (from a model) on a classification task."""
    import json
    import typing

    import matplotlib.backends.backend_pdf
    import numpy

    from ...engine.classify.evaluator import make_plots, make_table, run
    from ..utils import save_json_metadata, save_json_with_backup

    evaluation_file = output_folder / "evaluation.json"

    # register metadata
    save_json_metadata(
        output_file=evaluation_file.with_suffix(".meta.json"),
        predictions=str(predictions),
        output_folder=str(output_folder),
        threshold=threshold,
        binning=binning,
        plot=plot,
    )

    with predictions.open("r") as f:
        predict_data = json.load(f)

    if threshold in predict_data:
        # It is the name of a split on one of the two supported classifier
        # types. First run evaluation for reference dataset.
        from ...engine.classify.evaluator import maxf1_threshold

        use_threshold = maxf1_threshold(predict_data[threshold])
        logger.info(f"Setting --threshold={use_threshold:.5f}")

    else:
        # we try to convert it to float and complain if that is not possible
        try:
            use_threshold = float(threshold)
        except ValueError:
            raise click.BadParameter(
                f"""The value of --threshold=`{threshold}` does not match one
                of the database split names ({', '.join(predict_data.keys())})
                or can not be converted to a float. Check your input.""",
            )

    rng = numpy.random.default_rng(seed)

    results: dict[str, dict[str, typing.Any]] = dict()
    for k, v in predict_data.items():
        logger.info(f"Computing performance on split `{k}`...")
        results[k] = run(
            name=k,
            predictions=v,
            binning=int(binning) if binning.isnumeric() else binning,
            rng=rng,
            threshold_a_priori=use_threshold,
            credible_regions=credible_regions,
        )

    # records full result analysis to a JSON file
    logger.info(f"Saving evaluation results at `{str(evaluation_file)}`...")
    save_json_with_backup(evaluation_file, results)

    # Produces and records table
    table = make_table(results, "rst")
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
            for fig in make_plots(results):
                pdf.savefig(fig)
