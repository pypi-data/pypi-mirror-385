# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import typing

import click
from clapper.click import verbosity_option

from .logging import setup_cli_logger

# avoids X11/graphical desktop requirement when creating plots
__import__("matplotlib").use("agg")

logger = setup_cli_logger()


def _create_generic_figure(
    curves: dict[str, tuple[list[int], list[float]]],
    group: str,
) -> tuple:
    """Create a generic figure showing the evolution of a metric.

    This function will create a generic figure (one-size-fits-all kind of
    style) of a given metric across epochs.

    Parameters
    ----------
    curves
        A dictionary where keys represent all scalar names, and values
        correspond to a tuple that contains an array with epoch numbers (when
        values were taken), and the monitored values themselves.  These lists
        are pre-sorted by epoch number.
    group
        A scalar globs present in the existing tensorboard data that
        we are interested in for plotting.

    Returns
    -------
        A matplotlib figure and its axes.
    """

    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.ticker import MaxNLocator

    fig, ax = plt.subplots(1, 1)
    ax = typing.cast(Axes, ax)
    fig = typing.cast(Figure, fig)

    if len(curves) == 1:
        # there is only one curve, just plot it
        title, (epochs, values) = next(iter(curves.items()))
        ax.plot(epochs, values)

    else:
        # this is an aggregate plot, name things consistently
        labels = {k: k[len(group) - 1 :] for k in curves.keys()}
        title = group.rstrip("*").rstrip("/")
        for key, (epochs, values) in curves.items():
            ax.plot(epochs, values, label=labels[key])
        ax.legend(loc="best")

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title(title)
    ax.set_xlabel("Epoch")
    ax.set_ylabel(title)

    ax.grid(alpha=0.3)
    fig.tight_layout()

    return fig, ax


def _create_loss_figure(
    curves: dict[str, tuple[list[int], list[float]]],
    group: str,
) -> tuple:
    """Create a specific figure of the loss evolution.

    This function will create a specific, more detailed figure of the loss
    evolution plot where the curves will be enriched with vertical lines
    indicating the points where the lowest validation losses are detected.  The
    higher the point oppacity, the lower is the loss on the validation set.

    Parameters
    ----------
    curves
        A dictionary where keys represent all scalar names, and values
        correspond to a tuple that contains an array with epoch numbers (when
        values were taken), and the monitored values themselves.  These lists
        are pre-sorted by epoch number.
    group
        A scalar globs present in the existing tensorboard data that
        we are interested in for plotting.

    Returns
    -------
        A matplotlib figure and its axes.
    """

    fig, ax = _create_generic_figure(curves, group)

    if "loss/validation" in curves:
        points = sorted(zip(*curves["loss/validation"]), key=lambda x: x[1])[:4]

        # create the highlights for each point, with fading colours
        alpha_decay = 0.5
        alpha = 1.0
        for x, y in points:
            ax.axvline(
                x=x,
                color="red",
                alpha=alpha,
                linestyle=":",
                label=f"epoch {x} (val={y:.3g})",
            )
            alpha *= 1 - alpha_decay

    ax.legend(loc="best")
    return fig, ax


def _create_figures(
    data: dict[str, tuple[list[int], list[float]]],
    groups: list[str] = [
        "loss/*",
        "learning-rate",
        "memory-used-GB/cpu/*rss-GB/cpu/*",
        "vms-GB/cpu/*",
        "num-open-files/cpu/*",
        "num-processes/cpu/*",
        "percent-usage/cpu/*",
        # nvidia gpu
        "memory-percent/gpu/*",
        "memory-used-GB/gpu/*",
        "memory-free-GB/gpu/*",
        "percent-usage/gpu/*",
    ],
) -> list:
    """Generate figures for each metric in the dataframe.

    Each row of the dataframe corresponds to an epoch and each column to a metric.
    It is assumed that some metric names are of the form <metric>/<subset>.
    All subsets for a metric will be displayed on the same figure.

    Parameters
    ----------
    data
        A dictionary where keys represent all scalar names, and values
        correspond to a tuple that contains an array with epoch numbers (when
        values were taken), and the monitored values themselves.  These lists
        are pre-sorted by epoch number.
    groups
        A list of scalar globs present in the existing tensorboard data that
        we are interested in for plotting.  Values with multiple matches are
        drawn on the same plot.  Values that do not exist are ignored.

    Returns
    -------
    list
        List of matplotlib figures, one per metric.
    """

    import fnmatch

    figures = []

    for group in groups:
        curves = {k: data[k] for k in fnmatch.filter(data.keys(), group)}

        if len(curves) == 0:
            continue

        if group == "loss/*":
            fig, _ = _create_loss_figure(curves, group)
            figures.append(fig)
        else:
            fig, _ = _create_generic_figure(curves, group)
            figures.append(fig)

    return figures


@click.command(
    epilog="""Examples:

\b
    1. Analyze a training log and produces various plots:

       .. code:: sh

          mednet train-analysis -vv -l results/logs
""",
)
@click.option(
    "--logdir",
    "-l",
    help="Path to the directory containing the Tensorboard training logs",
    required=True,
    type=click.Path(dir_okay=True, exists=True, path_type=pathlib.Path),
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
    show_default=True,
    default="results",
)
@verbosity_option(logger=logger, expose_value=False)
def train_analysis(
    logdir: pathlib.Path,
    output_folder: pathlib.Path,
) -> None:  # numpydoc ignore=PR01
    """Create a plot for each metric in the training logs and saves them in a .pdf file."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    from ..utils.tensorboard import scalars_to_dict

    train_log_filename = "trainlog.pdf"
    train_log_file = pathlib.Path(output_folder) / train_log_filename

    data = scalars_to_dict(logdir)

    train_log_file.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(train_log_file) as pdf:
        for figure in _create_figures(data):
            pdf.savefig(figure)
            plt.close(figure)
