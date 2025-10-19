# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defines functionality for the evaluation of object detection predictions."""

import collections
import logging
import typing

import matplotlib.axes
import matplotlib.figure
import numpy
import numpy.typing
import tabulate
import torch
import torchvision.ops
from matplotlib import pyplot as plt

from ...models.detect.typing import Prediction

logger = logging.getLogger(__name__)


def _compute_iou_from_predictions(
    predictions: typing.Sequence[Prediction],
) -> list[list[tuple[int, float, int, float]]]:
    """Calculate the IOU for each **detected** bounding-box in predictions.

    This function will calculate the IOU (intersection over union) metric for each
    detected bounding-box (as in output by a model) in the prediction dataset.  It will
    then return a list of tuples, each matching a prediction, indicating the matched
    target, the IOU, the class and the model score.

    Parameters
    ----------
    predictions
        A list of predictions to consider for measurement.

    Returns
    -------
        A list containing lists of tuples, matching the order of **detected**
        bounding-boxes (as in output by a model). Each tuple contains the index of the
        matching target bounding box, the IOU between the target and said detected
        bounding-box, the class of the said target/detected bounding box, and finally
        the model score.

        In case there is no match for a particular detected bounding-box, the output
        table matching this would contain ``(-1, 0.0, <class>, 0.0)``.  This model
        output can be accounted as a "misdetection".
    """

    retval: list[list[tuple[int, float, int, float]]] = []

    for sample in predictions:
        name, targets, detections = sample

        # calculates IOU of all targets against all bounding boxes
        if detections:
            iou = torchvision.ops.box_iou(
                torch.tensor([k[0] for k in targets]),
                torch.tensor([k[0] for k in detections]),
            ).numpy()
        else:
            logger.warning(f"No detections for sample `{name}` were found.")
            retval.append(list())
            continue

        # we are only interested in the positions in which targets and detections have
        # matching labels - everything else can be set to zero on the IOU matrix
        iou *= numpy.equal.outer(
            [k[1] for k in targets], [k[1] for k in detections]
        ).astype(int)

        # the order of attributions need to go from highest to lowest score
        attribution_order = numpy.flip(numpy.argsort([k[2] for k in detections]))

        attributions: list[tuple[int, float, int, float]] = []
        for detection_index in attribution_order:
            max_iou_arg = iou[:, detection_index].argmax()
            if iou[max_iou_arg, detection_index] > 0.0:  # match
                attributions.append(
                    (
                        max_iou_arg,
                        iou[max_iou_arg, detection_index],
                        detections[detection_index][1],
                        detections[detection_index][2],
                    )
                )
                iou[max_iou_arg] = 0.0  # this (ground-truth) target has been attributed
            else:  # no match
                attributions.append((-1, 0.0, detections[detection_index][1], 0.0))

        retval.append(attributions)

    return retval


def run(
    predictions: typing.Sequence[Prediction],
    binning: str | int,
    iou_threshold: float | None = None,
) -> dict[str, typing.Any]:
    """Run inference and calculates measures for multilabel object detection.

    Parameters
    ----------
    predictions
        A list of predictions to consider for measurement.
    binning
        The binning algorithm to use for computing the bin widths and
        distribution for histograms.  Choose from algorithms supported by
        :py:func:`numpy.histogram`.
    iou_threshold
        IOU threshold by which we consider successful object detection. If set to
        ``None``, then apply no thresholding.

    Returns
    -------
        A dictionary containing the performance summary on the specified threshold,
        general performance curves (under the key ``curves``), and score histograms
        (under the key ``score-histograms``).
    """

    detailed_iou = _compute_iou_from_predictions(predictions)
    if iou_threshold is not None:
        filtered_iou = [[k for k in j if k[1] >= iou_threshold] for j in detailed_iou]
    else:
        filtered_iou = detailed_iou

    iou_histogram = dict(
        zip(
            ("hist", "bin_edges"),
            numpy.histogram(
                [k[1] for j in filtered_iou for k in j if k], bins=binning, range=(0, 1)
            ),
        )
    )

    # the mean-iou only accounts the IoU for matches - non-matches are ignored on this
    # metric (test: k[0] >= 0)
    mean_iou = numpy.nan_to_num(
        numpy.mean([k[1] for j in filtered_iou for k in j if k if k[0] >= 0])
    )
    classes = sorted(list(set([k[1] for j in predictions for k in j[1]])))

    # the mean-iou only accounts the IoU for matches - non-matches are ignored on this
    # metric (test: k[0] >= 0)
    mean_iou_per_class = {
        cl: numpy.nan_to_num(
            numpy.mean(
                [
                    k[1]
                    for j in filtered_iou
                    for k in j
                    if k and k[0] >= 0 and k[2] == cl
                ]
            )
        )
        for cl in classes
    }
    num_targets_per_class = collections.Counter(
        [k[1] for j in predictions for k in j[1]]
    )
    num_detections_per_class = collections.Counter(
        [k[2] for j in filtered_iou for k in j if k]
    )
    iou_per_class = [(k[2], k[1]) for j in filtered_iou for k in j if k]
    iou_per_class = {cl: [k[1] for k in iou_per_class if k[0] == cl] for cl in classes}  # type: ignore

    per_class_histogram = {
        cl: dict(
            zip(
                ("hist", "bin_edges"),
                numpy.histogram(iou_per_class[cl], bins=binning, range=(0, 1)),
            )
        )
        for cl in classes
    }

    return {
        "num-samples": len(predictions),
        "num-targets": sum([len(k[1]) for k in predictions]),
        "num-detections": len([k[2] for j in filtered_iou for k in j if k]),
        "mean-iou": mean_iou,
        "iou-histogram": iou_histogram,
        "per-class": {
            cl: {
                "mean-iou": mean_iou_per_class[cl],
                "num-targets": num_targets_per_class[cl],
                "num-detections": num_detections_per_class[cl],
            }
            for cl in classes
        },
        "per-class-iou-histogram": per_class_histogram,
    }


def make_table(
    data: typing.Mapping[str, typing.Mapping[str, typing.Any]],
    fmt: str,
) -> str:
    """Tabulate summaries from multiple splits.

    This function can properly tabulate the various summaries produced for all
    the splits in a prediction database.

    Parameters
    ----------
    data
        An iterable over all summary data collected.
    fmt
        One of the formats supported by `python-tabulate
        <https://pypi.org/project/tabulate/>`_.

    Returns
    -------
    str
        A string containing the tabulated information.
    """

    def _exclusion_condition(v: str) -> bool:
        return v not in ("iou-histogram", "per-class", "per-class-iou-histogram")

    # dump evaluation results in RST format to screen and file
    table_data = {}
    for k, v in data.items():
        table_data[k] = {kk: vv for kk, vv in v.items() if _exclusion_condition(kk)}

    example = next(iter(table_data.values()))
    headers = list(example.keys())
    table = [[k[h] for h in headers] for k in table_data.values()]

    # add subset names
    headers = ["subset"] + headers
    table = [[name] + k for name, k in zip(table_data.keys(), table)]

    return tabulate.tabulate(table, headers, tablefmt=fmt, floatfmt=".3f")


def _iou_histogram_plot(
    histograms: dict[str, numpy.typing.NDArray]
    | dict[int, dict[str, numpy.typing.NDArray]],
    title: str,
    threshold: float | None,
) -> matplotlib.figure.Figure:
    """Plot the normalized score distributions for all systems.

    Parameters
    ----------
    histograms
        A dictionary containing all histograms that should be inserted into the
        plot.  Each histogram should itself be setup as another dictionary
        containing the keys ``hist`` and ``bin_edges`` as returned by
        :py:func:`numpy.histogram`.
    title
        Title of the plot.
    threshold
        Shows where the threshold is in the figure.  If set to ``None``, then
        does not show the threshold line.

    Returns
    -------
    matplotlib.figure.Figure
        A single (matplotlib) plot containing the score distribution, ready to
        be saved to disk or displayed.
    """

    from matplotlib.ticker import MaxNLocator

    fig, ax = plt.subplots(1, 1)
    assert isinstance(fig, matplotlib.figure.Figure)
    ax = typing.cast(matplotlib.axes.Axes, ax)  # gets editor to behave

    # Here, we configure the "style" of our plot
    ax.set_xlim((0, 1))
    ax.set_title(title)
    ax.set_xlabel("Score")
    ax.set_ylabel("Count")

    # Only show ticks on the left and bottom spines
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.get_yaxis().set_major_locator(MaxNLocator(integer=True))

    # Setup the grid
    ax.grid(linestyle="--", linewidth=1, color="gray", alpha=0.2)
    ax.get_xaxis().grid(False)

    max_hist = 0
    has_labels = False

    if isinstance(next(iter(histograms.keys())), int):
        histograms = typing.cast(dict[int, dict[str, numpy.typing.NDArray]], histograms)
        # per-class diagram, requires labels
        for cl in histograms.keys():
            hist = histograms[cl]["hist"]
            bin_edges = histograms[cl]["bin_edges"]
            width = 0.7 * (bin_edges[1] - bin_edges[0])
            center = (bin_edges[:-1] + bin_edges[1:]) / 2
            ax.bar(center, hist, align="center", width=width, label=str(cl), alpha=0.7)
            max_hist = max(max_hist, hist.max())
            has_labels |= True
    else:
        # single histogram, no need for labels
        histograms = typing.cast(dict[str, numpy.typing.NDArray], histograms)
        hist = histograms["hist"]
        bin_edges = histograms["bin_edges"]
        width = 0.7 * (bin_edges[1] - bin_edges[0])
        center = (bin_edges[:-1] + bin_edges[1:]) / 2
        ax.bar(center, hist, align="center", width=width, alpha=0.7)
        max_hist = max(max_hist, hist.max())
        has_labels |= False

    # Detach axes from the plot
    ax.spines["left"].set_position(("data", -0.015))
    ax.spines["bottom"].set_position(("data", -0.015 * max_hist))

    if threshold is not None:
        # Adds threshold line (dotted red)
        ax.axvline(
            threshold,  # type: ignore
            color="red",
            lw=2,
            alpha=0.75,
            ls="dotted",
            label="IOU threshold",
        )
        has_labels |= True

    # Adds a nice legend
    if has_labels:
        ax.legend(
            fancybox=True,
            framealpha=0.7,
        )

    # Makes sure the figure occupies most of the possible space
    fig.tight_layout()

    return fig


def make_plots(
    results: dict[str, dict[str, typing.Any]], iou_threshold: float | None = None
) -> list:
    """Create plots for all curves and score distributions in ``results``.

    Parameters
    ----------
    results
        Evaluation data as returned by :py:func:`run`.
    iou_threshold
        IOU threshold by which we consider successful object detection.  If set, it is
        shown on plots.

    Returns
    -------
        A list of figures to record to file
    """

    retval = []

    # score plots
    for split_name, data in results.items():
        retval.append(
            _iou_histogram_plot(
                data["iou-histogram"],
                f"IOU distribution (split: {split_name})",
                threshold=iou_threshold,
            )
        )

        if len(data["per-class-iou-histogram"]) > 1:
            retval.append(
                _iou_histogram_plot(
                    data["per-class-iou-histogram"],
                    f"IOU distribution per class (split: {split_name})",
                    threshold=iou_threshold,
                )
            )

    return retval
