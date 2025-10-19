# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defines functionality for the evaluation of classification predictions."""

import logging
import typing
from collections.abc import Iterable

import credible.bayesian.metrics
import credible.curves
import credible.plot
import matplotlib.axes
import matplotlib.figure
import numpy
import numpy.typing
import sklearn.metrics
import tabulate
from matplotlib import pyplot as plt
from sklearn.preprocessing import LabelBinarizer

from ...models.classify.typing import Prediction

logger = logging.getLogger(__name__)


def eer_threshold(predictions: Iterable[Prediction]) -> float:
    """Calculate the (approximate) threshold leading to the equal error rate.

    For multi-label problems, calculate the EER threshold in the "micro" sense
    by first rasterizing all scores and labels (with :py:func:`numpy.ravel`),
    and then using this (large) 1D vector like in a binary classifier.

    Parameters
    ----------
    predictions
        An iterable of multiple
        :py:data:`.models.classify.typing.Prediction`'s.

    Returns
    -------
    float
        The EER threshold value.
    """

    from scipy.interpolate import interp1d
    from scipy.optimize import brentq

    y_scores = numpy.array([k[2] for k in predictions]).ravel()
    y_labels = numpy.array([k[1] for k in predictions]).ravel()

    fpr, tpr, thresholds = sklearn.metrics.roc_curve(y_labels, y_scores)

    eer = brentq(lambda x: 1.0 - x - interp1d(fpr, tpr)(x), 0.0, 1.0)
    return float(interp1d(fpr, thresholds)(eer))


def _get_centered_maxf1(
    f1_scores: numpy.typing.NDArray,
    thresholds: numpy.typing.NDArray,
) -> tuple[float, float]:
    """Return the centered max F1 score threshold when multiple thresholds give
    the same max F1 score.

    Parameters
    ----------
    f1_scores
        1D array of f1 scores.
    thresholds
        1D array of thresholds.

    Returns
    -------
    tuple(float, float)
        A tuple with the maximum F1-score and the "centered" threshold.
    """

    maxf1 = f1_scores.max()
    maxf1_indices = numpy.where(f1_scores == maxf1)[0]

    # If multiple thresholds give the same max F1 score
    if len(maxf1_indices) > 1:
        mean_maxf1_index = int(round(numpy.mean(maxf1_indices)))
    else:
        mean_maxf1_index = maxf1_indices[0]

    return maxf1, thresholds[mean_maxf1_index]


def maxf1_threshold(predictions: Iterable[Prediction]) -> float:
    """Calculate the threshold leading to the maximum F1-score on a precision-
    recall curve.

    For multi-label problems, calculate the maximum F1-core threshold in the
    "micro" sense by first rasterizing all scores and labels (with
    :py:func:`numpy.ravel`), and then using this (large) 1D vector like in a
    binary classifier.

    Parameters
    ----------
    predictions
        An iterable of multiple
        :py:data:`.models.classify.typing.Prediction`'s.

    Returns
    -------
    float
        The threshold value leading to the maximum F1-score on the provided set
        of predictions.
    """

    y_scores = numpy.array([k[2] for k in predictions]).ravel()
    y_labels = numpy.array([k[1] for k in predictions]).ravel()

    precision, recall, thresholds = sklearn.metrics.precision_recall_curve(
        y_labels,
        y_scores,
    )

    numerator = 2 * recall * precision
    denom = recall + precision
    f1_scores = numpy.divide(
        numerator,
        denom,
        out=numpy.zeros_like(denom),
        where=(denom != 0),
    )

    _, maxf1_threshold = _get_centered_maxf1(f1_scores, thresholds)
    return maxf1_threshold


def run_single(
    name: str,
    predictions: typing.Sequence[Prediction],
    binning: str | int,
    rng: numpy.random.Generator,
    threshold_a_priori: float | None = None,
    credible_regions: bool = False,
) -> dict[str, typing.Any]:
    """Run inference and calculates measures for binary or multilabel
    classification.

    For multi-label problems, calculate the metrics in the "micro" sense by
    first rasterizing all scores and labels (with :py:func:`numpy.ravel`), and
    then using this (large) 1D vector like in a binary classifier.

    Parameters
    ----------
    name
        The name of subset to load.
    predictions
        A list of predictions to consider for measurement.
    binning
        The binning algorithm to use for computing the bin widths and
        distribution for histograms.  Choose from algorithms supported by
        :py:func:`numpy.histogram`.
    rng
        An initialized numpy random number generator.
    threshold_a_priori
        A threshold to use, evaluated *a priori*, if must report single values.
        If this value is not provided, an *a posteriori* threshold is calculated
        on the input scores.  This is a biased estimator.
    credible_regions
        If set to ``True``, then returns also credible intervals via
        :py:mod:`credible.bayesian.metrics`. Notice the evaluation of ROC-AUC
        and Average Precision confidence margins can be rather slow for larger
        datasets.

    Returns
    -------
    dict[str, typing.Any]
        A dictionary containing the performance summary on the specified threshold,
        general performance curves (under the key ``curves``), and score histograms
        (under the key ``score-histograms``).
    """

    y_scores = numpy.array([k[2] for k in predictions]).ravel()
    y_labels = numpy.array([k[1] for k in predictions])
    ## ctype = classifier_type(y_labels)
    num_samples, num_classes = y_labels.shape
    y_labels = y_labels.ravel()

    neg_label = y_labels.min()
    pos_label = y_labels.max()

    use_threshold = threshold_a_priori
    if use_threshold is None:
        use_threshold = maxf1_threshold(predictions)
        logger.warning(
            f"User did not pass an *a priori* threshold for the evaluation "
            f"of split `{name}`.  Using threshold a posteriori (biased) with value "
            f"`{use_threshold:.4f}`",
        )

    y_predictions = numpy.where(y_scores >= use_threshold, pos_label, neg_label)

    summary = dict(
        num_samples=num_samples,
        num_classes=num_classes,
        threshold=use_threshold,
        threshold_a_posteriori=(threshold_a_priori is None),
        precision=sklearn.metrics.precision_score(
            y_labels, y_predictions, pos_label=pos_label
        ),
        recall=sklearn.metrics.recall_score(
            y_labels, y_predictions, pos_label=pos_label
        ),
        f1=sklearn.metrics.f1_score(y_labels, y_predictions, pos_label=pos_label),
        average_precision=sklearn.metrics.average_precision_score(
            y_labels, y_scores, pos_label=pos_label
        ),
        specificity=sklearn.metrics.recall_score(
            y_labels, y_predictions, pos_label=neg_label
        ),
        roc_auc=sklearn.metrics.roc_auc_score(y_labels, y_scores),
        accuracy=sklearn.metrics.accuracy_score(y_labels, y_predictions),
    )

    if credible_regions:
        logger.info(
            f"Computing credible regions for metrics on split `{name}` "
            f"(samples = {len(predictions)}) - "
            f"note this can be slow on very large datasets..."
        )
        f1 = credible.bayesian.metrics.f1_score(y_labels, y_predictions, rng=rng)
        roc_auc = credible.bayesian.metrics.roc_auc_score(y_labels, y_scores)
        precision = credible.bayesian.metrics.precision_score(y_labels, y_predictions)
        recall = credible.bayesian.metrics.recall_score(y_labels, y_predictions)
        average_precision = credible.bayesian.metrics.average_precision_score(
            y_labels, y_scores
        )
        specificity = credible.bayesian.metrics.specificity_score(
            y_labels, y_predictions
        )
        accuracy = credible.bayesian.metrics.accuracy_score(y_labels, y_predictions)

        summary.update(
            dict(
                precision_mean=precision[0],
                precision_mode=precision[1],
                precision_lo=precision[2],
                precision_hi=precision[3],
                recall_mean=recall[0],
                recall_mode=recall[1],
                recall_lo=recall[2],
                recall_hi=recall[3],
                f1_mean=f1[0],
                f1_mode=f1[1],
                f1_lo=f1[2],
                f1_hi=f1[3],
                average_precision_exact=average_precision[0],
                average_precision_lo=average_precision[1],
                average_precision_hi=average_precision[2],
                specificity_mean=specificity[0],
                specificity_mode=specificity[1],
                specificity_lo=specificity[2],
                specificity_hi=specificity[3],
                roc_auc_exact=roc_auc[0],
                roc_auc_lo=roc_auc[1],
                roc_auc_hi=roc_auc[2],
                accuracy_mean=accuracy[0],
                accuracy_mode=accuracy[1],
                accuracy_lo=accuracy[2],
                accuracy_hi=accuracy[3],
            )
        )

    # curves: ROC and precision recall
    summary["curves"] = dict(
        roc=dict(
            zip(
                ("fpr", "tpr", "thresholds"),
                sklearn.metrics.roc_curve(
                    y_labels,
                    y_scores,
                    pos_label=pos_label,
                ),
            ),
        ),
        precision_recall=dict(
            zip(
                ("precision", "recall", "thresholds"),
                sklearn.metrics.precision_recall_curve(
                    y_labels,
                    y_scores,
                    pos_label=pos_label,
                ),
            ),
        ),
    )

    # score histograms
    # what works: <integer>, doane*, scott, stone, rice*, sturges*, sqrt
    # what does not work: auto, fd
    summary["score-histograms"] = dict(
        positives=dict(
            zip(
                ("hist", "bin_edges"),
                numpy.histogram(
                    y_scores[y_labels == pos_label],
                    bins=binning,
                    range=(0, 1),
                ),
            ),
        ),
        negatives=dict(
            zip(
                ("hist", "bin_edges"),
                numpy.histogram(
                    y_scores[y_labels == neg_label],
                    bins=binning,
                    range=(0, 1),
                ),
            ),
        ),
    )

    return summary


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
        return not (
            v in ("curves", "score-histograms", "confusion_matrix")
            or v.endswith(
                ("_mean", "_mode", "_hi", "_lo", "_exact", "_per_class", "_micro")
            )
        )

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


def _score_plot(
    histograms: dict[str, dict[str, numpy.typing.NDArray]],
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
    for name in histograms.keys():
        hist = histograms[name]["hist"]
        bin_edges = histograms[name]["bin_edges"]
        width = 0.7 * (bin_edges[1] - bin_edges[0])
        center = (bin_edges[:-1] + bin_edges[1:]) / 2
        ax.bar(center, hist, align="center", width=width, label=name, alpha=0.7)
        max_hist = max(max_hist, hist.max())

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
            label="threshold",
        )

    # Adds a nice legend
    ax.legend(
        fancybox=True,
        framealpha=0.7,
    )

    # Makes sure the figure occupies most of the possible space
    fig.tight_layout()

    return fig


def make_plots_single(results: dict[str, dict[str, typing.Any]]) -> list:
    """Create plots for all curves and score distributions in ``results``.

    Parameters
    ----------
    results
        Evaluation data as returned by :py:func:`run_single`.

    Returns
    -------
        A list of figures to record to file
    """

    retval = []

    with credible.plot.tight_layout(
        ("False Positive Rate", "True Positive Rate"), "ROC"
    ) as (fig, ax):
        for split_name, data in results.items():
            _auroc = credible.curves.area_under_the_curve(
                (data["curves"]["roc"]["fpr"], data["curves"]["roc"]["tpr"]),
            )
            ax.plot(
                data["curves"]["roc"]["fpr"],
                data["curves"]["roc"]["tpr"],
                label=f"{split_name} (AUC: {_auroc:.2f})",
            )
        ax.legend(loc="best", fancybox=True, framealpha=0.7)
        retval.append(fig)

    with credible.plot.tight_layout_f1iso(
        ("Recall", "Precision"), "Precison-Recall"
    ) as (fig, ax):
        for split_name, data in results.items():
            _ap = credible.curves.average_metric(
                (data["precision"], data["recall"]),
            )
            ax.plot(
                data["curves"]["precision_recall"]["recall"],
                data["curves"]["precision_recall"]["precision"],
                label=f"{split_name} (AP: {_ap:.2f})",
            )
        ax.legend(loc="best", fancybox=True, framealpha=0.7)
        retval.append(fig)

    # score plots
    for split_name, data in results.items():
        score_fig = _score_plot(
            data["score-histograms"],
            f"Score distribution (split: {split_name})",
            data["threshold"],
        )
        retval.append(score_fig)

    return retval


def run_multi(
    predictions: typing.Sequence[Prediction],
) -> dict[str, typing.Any]:
    """Run inference and calculates measures for multiclass classification.

    It computes the recall, precision, f1, auc and aupr for each single class
    and also with both macro and micro averaging. ROC curves are all computed
    following the OvR scheme macro-averaged.

    Parameters
    ----------
    predictions
        A list of predictions to consider for measurement.

    Returns
    -------
    dict[str, typing.Any]
        A dictionary containing the performance summary, general performance curves
        (under the key ``curves``), and confusion matrices (under the key
        ``confusion_matrix``).
    """

    y_probabilities = numpy.array([k[2] for k in predictions])
    y_labels = numpy.array([k[1] for k in predictions])

    num_samples = y_labels.size
    num_classes = numpy.max(y_labels) + 1

    y_labels = y_labels.ravel()

    y_predictions = numpy.argmax(y_probabilities, axis=1)

    summary = dict(
        num_samples=num_samples,
        num_classes=num_classes,
        precision_per_class=sklearn.metrics.precision_score(
            y_labels, y_predictions, average=None
        ),
        precision_macro=sklearn.metrics.precision_score(
            y_labels, y_predictions, average="macro"
        ),
        precision_micro=sklearn.metrics.precision_score(
            y_labels, y_predictions, average="micro"
        ),
        recall_per_class=sklearn.metrics.recall_score(
            y_labels, y_predictions, average=None
        ),
        recall_macro=sklearn.metrics.recall_score(
            y_labels, y_predictions, average="macro"
        ),
        recall_micro=sklearn.metrics.recall_score(
            y_labels, y_predictions, average="micro"
        ),
        f1_per_class=sklearn.metrics.f1_score(y_labels, y_predictions, average=None),
        f1_macro=sklearn.metrics.f1_score(y_labels, y_predictions, average="macro"),
        f1_micro=sklearn.metrics.f1_score(y_labels, y_predictions, average="micro"),
        average_precision_per_class=sklearn.metrics.average_precision_score(
            y_labels, y_probabilities, average=None
        ),
        average_precision_macro=sklearn.metrics.average_precision_score(
            y_labels, y_probabilities, average="macro"
        ),
        average_precision_micro=sklearn.metrics.average_precision_score(
            y_labels, y_probabilities, average="micro"
        ),
        roc_auc_per_class=sklearn.metrics.roc_auc_score(
            y_labels, y_probabilities, average=None, multi_class="ovr"
        ),
        roc_auc_macro=sklearn.metrics.roc_auc_score(
            y_labels, y_probabilities, average="macro", multi_class="ovr"
        ),
        roc_auc_micro=sklearn.metrics.roc_auc_score(
            y_labels, y_probabilities, average="micro", multi_class="ovr"
        ),
        accuracy=sklearn.metrics.accuracy_score(y_labels, y_predictions),
        # I would like to add the MCP and IMCP scores
    )

    # curves: ROC and precision recall
    summary["curves"] = dict(
        {
            **{f"roc_{class_id}": dict() for class_id in range(num_classes)},
            **{
                f"precision_recall_{class_id}": dict()
                for class_id in range(num_classes)
            },
        }
    )

    # Binarize the labels
    y_labels_onehot = LabelBinarizer().fit_transform(y_labels)

    # Store one roc and precision recall curve for each class
    # In the meanwhile compute the macro ROC curve
    fpr_grid_macro = numpy.linspace(0.0, 1.0, 1000)
    mean_tpr = numpy.zeros_like(fpr_grid_macro)

    for class_id in range(num_classes):
        summary["curves"][f"roc_{class_id}"] = dict(
            zip(
                ("fpr", "tpr", "thresholds"),
                sklearn.metrics.roc_curve(
                    y_labels_onehot[:, class_id],  # type: ignore
                    y_probabilities[:, class_id],
                ),
            ),
        )
        summary["curves"][f"precision_recall_{class_id}"] = dict(
            zip(
                ("precision", "recall", "thresholds"),
                sklearn.metrics.precision_recall_curve(
                    y_labels_onehot[:, class_id],  # type: ignore
                    y_probabilities[:, class_id],
                ),
            ),
        )
        mean_tpr += numpy.interp(
            fpr_grid_macro,
            summary["curves"][f"roc_{class_id}"]["fpr"],
            summary["curves"][f"roc_{class_id}"]["tpr"],
        )  # linear interpolation

    # Average it and compute AUC macro
    mean_tpr /= num_classes

    summary["curves"]["roc_fpr_macro"] = fpr_grid_macro  # type: ignore
    summary["curves"]["roc_tpr_macro"] = mean_tpr

    # Confusion matrix
    cm = sklearn.metrics.confusion_matrix(y_labels, y_predictions)
    summary["confusion_matrix"] = cm

    return summary


def make_plots_multi(results: dict[str, dict[str, typing.Any]]) -> list:
    """Create plots for all curves and score distributions in ``results``.

    Parameters
    ----------
    results
        Evaluation data as returned by :py:func:`run_multi`.

    Returns
    -------
        A list of figures to record to file
    """

    retval = []

    # ROC macro averaged (OvR). One ROC for each split
    with credible.plot.tight_layout(
        ("False Positive Rate", "True Positive Rate"), "Macro-averaged One-vs-Rest ROC"
    ) as (fig, ax):
        for split_name, data in results.items():
            _auroc = credible.curves.area_under_the_curve(
                (data["curves"]["roc_fpr_macro"], data["curves"]["roc_tpr_macro"]),
            )
            ax.plot(
                data["curves"]["roc_fpr_macro"],
                data["curves"]["roc_tpr_macro"],
                label=f"{split_name} (AUC: {_auroc:.2f})",
            )
        ax.legend(loc="best", fancybox=True, framealpha=0.7)
        retval.append(fig)

    # Plot all OvR ROC curves per class together. Each split has its own plot with num_classes ROC curves
    for split_name, data in results.items():
        with credible.plot.tight_layout(
            ("False Positive Rate", "True Positive Rate"),
            f"{split_name} - OvR ROC for each class",
        ) as (fig, ax):
            for class_id in range(data["num_classes"]):
                _auroc = credible.curves.area_under_the_curve(
                    (
                        data["curves"][f"roc_{class_id}"]["fpr"],
                        data["curves"][f"roc_{class_id}"]["tpr"],
                    ),
                )
                ax.plot(
                    data["curves"][f"roc_{class_id}"]["fpr"],
                    data["curves"][f"roc_{class_id}"]["tpr"],
                    label=f"Class {class_id} (AUC: {_auroc:.2f})",
                )
            ax.legend(loc="best", fancybox=True, framealpha=0.7)
            retval.append(fig)

    # Plot all Precision-Recall curves per class together.
    for split_name, data in results.items():
        with credible.plot.tight_layout(
            ("Recall", "Precision"),
            f"{split_name} - Precision-Recall curve for each class",
        ) as (fig, ax):
            for class_id in range(data["num_classes"]):
                _ap = credible.curves.average_metric(
                    (
                        data["curves"][f"precision_recall_{class_id}"]["precision"],
                        data["curves"][f"precision_recall_{class_id}"]["recall"],
                    ),
                )
                ax.plot(
                    data["curves"][f"precision_recall_{class_id}"]["recall"],
                    data["curves"][f"precision_recall_{class_id}"]["precision"],
                    label=f"Class {class_id} (AP: {_ap:.2f})",
                )
            ax.legend(loc="best", fancybox=True, framealpha=0.7)
            retval.append(fig)

    # Plot the confusion matrices. One for each split
    for split_name, data in results.items():
        fig, ax = plt.subplots()
        disp = sklearn.metrics.ConfusionMatrixDisplay(
            confusion_matrix=data["confusion_matrix"]
        )
        disp.plot(ax=ax, cmap=plt.colormaps.get_cmap("Blues"))
        ax.set_title(f"Confusion Matrix - {split_name}")
        retval.append(fig)

    return retval


def run(
    name: str,
    predictions: typing.Sequence[Prediction],
    binning: str | int,
    rng: numpy.random.Generator,
    threshold_a_priori: float | None = None,
    credible_regions: bool = False,
) -> dict[str, typing.Any]:
    """Run inference and calculates measures for binary, multilabel or multiclass
    classification. It autocmatically detects the problem type, and route the arguments
    to the pertinent functions (:py:func:`run_single` for binary and multilabel,
    :py:func:`run_multi` for multiclass classification problem).

    For multi-label problems, calculate the metrics in the "micro" sense by
    first rasterizing all scores and labels (with :py:func:`numpy.ravel`), and
    then using this (large) 1D vector like in a binary classifier.

    Parameters
    ----------
    name
        The name of subset to load.
    predictions
        A list of predictions to consider for measurement.
    binning
        The binning algorithm to use for computing the bin widths and
        distribution for histograms.  Choose from algorithms supported by
        :py:func:`numpy.histogram`.
    rng
        An initialized numpy random number generator.
    threshold_a_priori
        A threshold to use, evaluated *a priori*, if must report single values.
        If this value is not provided, an *a posteriori* threshold is calculated
        on the input scores.  This is a biased estimator.
    credible_regions
        If set to ``True``, then returns also credible intervals via
        :py:mod:`credible.bayesian.metrics`. Notice the evaluation of ROC-AUC
        and Average Precision confidence margins can be rather slow for larger
        datasets.

    Returns
    -------
    dict[str, typing.Any]
        For **binary** and **multilabel** classification problem: a dictionary
        containing the performance summary on the specified threshold, general
        performance curves (under the key ``curves``), and score histograms
        (under the key ``score-histograms``).
        For **multiclass** classification problem: a dictionary containing the
        performance summary, general performance curves (under the key ``curves``),
        and confusion matrices (under the key ``confusion_matrix``).
    """

    sample = predictions[0]
    target_shape = len(sample[1])
    prediction_shape = len(sample[2])

    # Binary and Multilabel problems have same target and prediction shape: (1,) for binary and (C,) for multilabel
    # For Multiclass scenario the prediction shape is (C,) but the target is (1,) since it is a single value between [0, C-1]
    multiclass_problem = prediction_shape != target_shape
    if multiclass_problem:
        summary = run_multi(
            predictions=predictions,
        )
    else:
        summary = run_single(
            name=name,
            predictions=predictions,
            binning=binning,
            rng=rng,
            threshold_a_priori=threshold_a_priori,
            credible_regions=credible_regions,
        )

    return summary


def make_plots(results: dict[str, dict[str, typing.Any]]) -> list:
    """Create plots for all curves and score distributions in ``results``.

    Parameters
    ----------
    results
        Evaluation data as returned by :py:func:`run`.

    Returns
    -------
        A list of figures to record to file
    """

    multiclass = True
    for _, data in results.items():
        if "score-histograms" in data.keys():
            multiclass = False
            break

    if multiclass:
        retval = make_plots_multi(
            results=results,
        )
    else:
        retval = make_plots_single(
            results=results,
        )

    return retval
