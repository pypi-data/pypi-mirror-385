# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Common utilities for saliency generation and analysis tasks."""

import typing

import matplotlib.figure
import numpy
import numpy.typing
import tabulate


def extract_statistics(
    data: list[tuple[str, int, float, float, float]],
    index: int,
) -> dict[str, typing.Any]:
    """Extract all meaningful statistics from a reconciled statistics set.

    Parameters
    ----------
    data
        A list of tuples each containing a sample name, target, and values
        produced by completeness and interpretability analysis.
    index
        The index of the tuple contained in ``data`` that should be extracted.

    Returns
    -------
        A dictionary containing the following elements:

            * ``values``: A list of values corresponding to the index on the data
            * ``mean``: The mean of the value listdir
            * ``stdev``: The standard deviation of the value list
            * ``quartiles``: The 25%, 50% (median), and 75% quartile of values
            * ``decreasing_scores``: A list of sample names and labels in
              decreasing value.
    """

    val = numpy.array([k[index] for k in data])
    return dict(
        values=val,
        mean=val.mean(),
        stdev=val.std(ddof=1),  # unbiased estimator
        quartiles={
            25: numpy.percentile(val, 25),  # type: ignore
            50: numpy.median(val),  # type: ignore
            75: numpy.percentile(val, 75),  # type: ignore
        },
        decreasing_scores=[
            (k[0], k[index]) for k in sorted(data, key=lambda x: x[index], reverse=True)
        ],
    )


def make_table(
    results: dict[str, list[typing.Any]],
    indexes: dict[int, str],
    format_: str,
) -> str:
    """Summarize results obtained by interpretability or completeness analysis
    in a table.

    Parameters
    ----------
    results
        The results to be summarized.
    indexes
        A dictionary where keys are indexes in each sample of ``results``, and
        values are a (possibly abbreviated) name to be used in table headers.
    format_
        The table format.

    Returns
    -------
        A table, formatted following ``format_`` and containing the
        various quartile informations for each split and metric.
    """

    headers = ["subset", "samples"]
    for idx, name in indexes.items():
        headers += [
            f"{name}[mean]",
            f"{name}[std]",
            f"{name}[25%]",
            f"{name}[50%]",
            f"{name}[75%]",
        ]

    data = []

    for k, v in results.items():
        samples = [s for s in v if len(s) != 2]
        row = [k, len(samples)]
        for idx in indexes.keys():
            stats = extract_statistics(samples, index=idx)
            row += [
                stats["mean"],
                stats["stdev"],
                stats["quartiles"][25],
                stats["quartiles"][50],
                stats["quartiles"][75],
            ]
        data.append(row)

    return tabulate.tabulate(data, headers, tablefmt=format_, floatfmt=".3f")


def make_histogram(
    name: str,
    values: numpy.typing.NDArray,
    xlim: tuple[float, float] | None = None,
    title: None | str = None,
) -> matplotlib.figure.Figure:
    """Build an histogram of values.

    Parameters
    ----------
    name
        Name of the variable to be histogrammed (will appear in the figure).
    values
        Values to be histogrammed.
    xlim
        A tuple representing the X-axis maximum and minimum to plot. If not
        set, then use the bin boundaries.
    title
        A title to set on the histogram.

    Returns
    -------
        A matplotlib figure containing the histogram.
    """

    from matplotlib import pyplot

    fig, ax = pyplot.subplots(1)
    ax = typing.cast(matplotlib.figure.Axes, ax)
    ax.set_xlabel(name)
    ax.set_ylabel("Frequency")

    if title is not None:
        ax.set_title(title)
    else:
        ax.set_title(f"{name} Frequency Histogram")

    n, bins, _ = ax.hist(values, bins="auto", density=True, alpha=0.7)

    if xlim is not None:
        ax.spines.bottom.set_bounds(*xlim)
    else:
        ax.spines.bottom.set_bounds(bins[0], bins[-1])

    ax.spines.left.set_bounds(0, n.max())
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)

    ax.grid(linestyle="--", linewidth=1, color="gray", alpha=0.3)

    # draw median and quartiles
    quartile = numpy.percentile(values, [25, 50, 75])
    ax.axvline(
        quartile[0],
        color="green",
        linestyle="--",
        label="Q1",
        alpha=0.5,
    )
    ax.axvline(quartile[1], color="red", label="median", alpha=0.5)
    ax.axvline(
        quartile[2],
        color="green",
        linestyle="--",
        label="Q3",
        alpha=0.5,
    )

    return fig  # type: ignore


def make_plots(
    results: dict[str, list[typing.Any]],
    indexes: dict[int, str],
    xlim: tuple[float, float] | None = None,
) -> list[matplotlib.figure.Figure]:
    """Plot histograms for a particular variable, across all datasets.

    Parameters
    ----------
    results
        The results to be plotted.
    indexes
        A dictionary where keys are indexes in each sample of ``results``, and
        values are a (possibly abbreviated) name to be used in figure titles
        and axes.
    xlim
        Limits for histogram plotting.

    Returns
    -------
        Matplotlib figures containing histograms for each dataset within
        ``results`` and named variables in ``indexes``.
    """

    retval = []

    for k, v in results.items():
        samples = [s for s in v if len(s) != 2]
        for idx, name in indexes.items():
            val = numpy.array([s[idx] for s in samples])
            retval.append(
                make_histogram(
                    name, val, xlim=xlim, title=f"{name} Frequency Histogram (@ {k})"
                )
            )

    return retval
