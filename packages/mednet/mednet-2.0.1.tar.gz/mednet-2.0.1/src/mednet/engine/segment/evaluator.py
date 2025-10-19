# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Defines functionality for the evaluation of predictions."""

import json
import logging
import pathlib
import typing

import credible.curves
import credible.plot
import h5py
import numpy
import numpy.typing
import tabulate
from tqdm import tqdm

logger = logging.getLogger(__name__)

SUPPORTED_METRIC_TYPE = typing.Literal[
    "precision", "recall", "specificity", "accuracy", "jaccard", "f1"
]
"""Supported metrics for evaluation of counts."""


def _tricky_division(n: float, d: float):
    """Divide n by d, or 0.0 in case of a division by zero.

    Parameters
    ----------
    n
        The number to divide.
    d
        The divisor.

    Returns
    -------
        Result of the division.
    """

    return n / (d + (d == 0))


def precision(tp: int, fp: int, tn: int, fn: int) -> float:
    """Calculate the precision given true/false positive/negative counts.

    P, AKA positive predictive value (PPV).  It corresponds arithmetically to
    ``tp/(tp+fp)``.  In the case ``tp+fp == 0``, this function returns zero for
    precision.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        The precision.
    """
    return _tricky_division(tp, tp + fp)


def recall(tp: int, fp: int, tn: int, fn: int) -> float:
    """Calculate the recall given true/false positive/negative counts.

    R, AKA sensitivity, hit rate, or true positive rate (TPR).  It corresponds
    arithmetically to ``tp/(tp+fn)``.  In the special case where ``tp+fn ==
    0``, this function returns zero for recall.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        The recall.
    """
    return _tricky_division(tp, tp + fn)


def specificity(tp: int, fp: int, tn: int, fn: int) -> float:
    """Calculate the specificity given true/false positive/negative counts.

    S, AKA selectivity or true negative rate (TNR).  It corresponds
    arithmetically to ``tn/(tn+fp)``.  In the special case where ``tn+fp ==
    0``, this function returns zero for specificity.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        The specificity.
    """
    return _tricky_division(tn, fp + tn)


def accuracy(tp: int, fp: int, tn: int, fn: int) -> float:
    """Calculate the accuracy given true/false positive/negative counts.

    A, see `Accuracy
    <https://en.wikipedia.org/wiki/Evaluation_of_binary_classifiers>`_. is the
    proportion of correct predictions (both true positives and true negatives)
    among the total number of pixels examined.  It corresponds arithmetically
    to ``(tp+tn)/(tp+tn+fp+fn)``.  This measure includes both true-negatives
    and positives in the numerator, what makes it sensitive to data or regions
    without annotations.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        The accuracy.
    """
    return _tricky_division(tp + tn, tp + fp + fn + tn)


def jaccard(tp: int, fp: int, tn: int, fn: int) -> float:
    """Calculate the Jaccard index given true/false positive/negative counts.

    J, see `Jaccard Index or Similarity
    <https://en.wikipedia.org/wiki/Jaccard_index>`_.  It corresponds
    arithmetically to ``tp/(tp+fp+fn)``.  In the special case where ``tn+fp+fn
    == 0``, this function returns zero for the Jaccard index. The Jaccard index
    depends on a TP-only numerator, similarly to the F1 score.  For regions
    where there are no annotations, the Jaccard index will always be zero,
    irrespective of the model output.  Accuracy may be a better proxy if one
    needs to consider the true abscence of annotations in a region as part of
    the measure.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        The Jaccard index.
    """
    return _tricky_division(tp, tp + fp + fn)


def f1_score(tp: int, fp: int, tn: int, fn: int) -> float:
    """Calculate the F1 score given true/false positive/negative counts.

    F1, see `F1-score <https://en.wikipedia.org/wiki/F1_score>`_.  It
    corresponds arithmetically to ``2*P*R/(P+R)`` or ``2*tp/(2*tp+fp+fn)``. In
    the special case where ``P+R == (2*tp+fp+fn) == 0``, this function returns
    zero for the Jaccard index.  The F1 or Dice score depends on a TP-only
    numerator, similarly to the Jaccard index.  For regions where there are no
    annotations, the F1-score will always be zero, irrespective of the model
    output.  Accuracy may be a better proxy if one needs to consider the true
    abscence of annotations in a region as part of the measure.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        The F1-score.
    """
    return _tricky_division(2 * tp, (2 * tp) + fp + fn)


_METRIC_MAPPING = {
    k: v
    for k, v in zip(
        typing.get_args(SUPPORTED_METRIC_TYPE),
        [precision, recall, specificity, accuracy, jaccard, f1_score],
    )
}
"""Maps supported metric names and callables implementing them."""


def name2metric(
    name: SUPPORTED_METRIC_TYPE,
) -> typing.Callable[[int, int, int, int], float]:
    """Convert a string name to a callable for summarizing counts.

    Parameters
    ----------
    name
        The name of the metric to be looked up.

    Returns
    -------
        A callable that summarizes counts into single floating-point number.
    """
    return _METRIC_MAPPING[name]


def all_metrics(tp: int, fp: int, tn: int, fn: int) -> list[float]:
    """Compute all available metrics at once.

    Parameters
    ----------
    tp
        True positive count, AKA "hit".
    fp
        False positive count, AKA "false alarm", or "Type I error".
    tn
        True negative count, AKA "correct rejection".
    fn
        False Negative count, AKA "miss", or "Type II error".

    Returns
    -------
        All supported metrics in the order defined by
        :py:obj:`SUPPORTED_METRIC_TYPE`.
    """
    return [k(tp, fp, tn, fn) for k in _METRIC_MAPPING.values()]


def tfpn_masks(
    pred: numpy.typing.NDArray[numpy.float32],
    gt: numpy.typing.NDArray[numpy.bool_],
    threshold: float,
) -> tuple[
    numpy.typing.NDArray[numpy.bool_],
    numpy.typing.NDArray[numpy.bool_],
    numpy.typing.NDArray[numpy.bool_],
    numpy.typing.NDArray[numpy.bool_],
]:
    """Calculate true and false positives and negatives.

    All input arrays should have matching sizes.

    Parameters
    ----------
    pred
        Pixel-wise predictions as output by your model.
    gt
        Ground-truth (annotations).
    threshold
        A particular threshold in which to calculate the performance
        measures.  Values at this threshold are counted as positives.

    Returns
    -------
    tp
        Boolean array with true positives, considering all observations.
    fp
        Boolean array with false positives, considering all observations.
    tn
        Boolean array with true negatives, considering all observations.
    fn
        Boolean array with false negatives, considering all observations.
    """

    binary_pred = pred >= threshold
    tp = numpy.logical_and(binary_pred, gt)
    fp = numpy.logical_and(binary_pred, numpy.logical_not(gt))
    tn = numpy.logical_and(numpy.logical_not(binary_pred), numpy.logical_not(gt))
    fn = numpy.logical_and(numpy.logical_not(binary_pred), gt)
    return tp, fp, tn, fn


def get_counts_for_threshold(
    pred: numpy.typing.NDArray[numpy.float32],
    gt: numpy.typing.NDArray[numpy.bool_],
    mask: numpy.typing.NDArray[numpy.bool_],
    threshold: float,
) -> tuple[int, int, int, int]:
    """Calculate counts on one single sample, for a specific threshold.

    Parameters
    ----------
    pred
        Array with pixel-wise predictions.
    gt
        Array with ground-truth (annotations).
    mask
        Array with region mask marking parts to ignore.
    threshold
        A particular threshold in which to calculate the performance
        measures.

    Returns
    -------
        The true positives, false positives, true negatives and false
        negatives, in that order.
    """

    tp, fp, tn, fn = tfpn_masks(pred, gt, threshold)
    tp = numpy.logical_and(tp, mask)
    fp = numpy.logical_and(fp, mask)
    tn = numpy.logical_and(tn, mask)
    fn = numpy.logical_and(fn, mask)
    return tp.sum(), fp.sum(), tn.sum(), fn.sum()


def load_count(
    prediction_path: pathlib.Path,
    predictions: typing.Sequence[str],
    thresholds: numpy.typing.NDArray[numpy.float64],
) -> numpy.typing.NDArray[numpy.uint64]:
    """Count true/false positive/negatives for the subset.

    This function will load predictions from their store location and will
    **cumulatively** count the number of true positives, false positives, true
    negatives and false negatives across the various ``thresholds``.  This
    alternative provides a memory-bound way to compute the performance of
    splits with potentially very large images or including a large/very large
    number of samples.  Unfortunately, sklearn does not provide functions to
    compute standard metrics from true/false positive/negative counts, which
    implies one needs to make use of further functions defined in this module
    to compute such metrics.  Alternatively, you may look into
    :py:func:`load_predictions`, if you want to use sklearn functions to
    compute metrics.

    Parameters
    ----------
    prediction_path
        Base directory where the prediction files (HDF5) were stored.
    predictions
        A list of relative sample prediction paths to consider for measurement.
    thresholds
        A sequence of thresholds to be applied on ``predictions``, when
        evaluating true/false positive/negative counts.

    Returns
    -------
        A 2-D array with shape ``(len(thresholds), 4)``, where each row
        contains to the counts of true positives, false positives, true
        negatives and false negatives, for the related threshold, and for the
        **whole dataset**.
    """
    data = numpy.zeros((len(thresholds), 4), dtype=numpy.uint64)
    for sample in tqdm(predictions, desc="sample"):
        with h5py.File(prediction_path / sample[1], "r") as f:
            pred = numpy.array(f["prediction"])  # float32
            gt = numpy.array(f["target"])  # boolean
            mask = numpy.array(f["mask"])  # boolean
        data += numpy.array(
            [get_counts_for_threshold(pred, gt, mask, k) for k in thresholds],
            dtype=numpy.uint64,
        )
    return data


def load_predictions(
    prediction_path: pathlib.Path,
    predictions: typing.Sequence[str],
) -> tuple[numpy.typing.NDArray[numpy.float32], numpy.typing.NDArray[numpy.bool_]]:
    """Load predictions and ground-truth from HDF5 files.

    Loading pixel-data as simple binary predictions with associated labels
    allows using sklearn library to compute most metrics defined in this
    module.  Note however that computing metrics this way requires
    pre-allocation of a potentially large vector, which depends on the number
    of samples and the size of said samples.  This may not work well for very
    large datasets of large/very large images.  Currently, the evaluation
    system uses :py:func:`load_count` instead, which loads and pre-computes the
    number of true/false positives/negatives using a list of candidate
    thresholds.

    Parameters
    ----------
    prediction_path
        Base directory where the prediction files (HDF5) were stored.
    predictions
        A list of relative sample prediction paths to consider for measurement.

    Returns
    -------
        Two 1-D arrays containing a linearized version of pixel predictions
        (probability) and matching ground-truth.
    """

    # peak prediction size and number of samples
    with h5py.File(prediction_path / predictions[0][1], "r") as f:
        data: h5py.Dataset = typing.cast(h5py.Dataset, f["prediction"])
        elements = numpy.array(data.shape).prod()
    size = len(predictions) * elements
    logger.info(
        f"Data loading will require ({elements} x {len(predictions)} x 5 =) "
        f"{size*5/(1024*1024):.0f} MB of RAM"
    )

    # now load the data
    pred_array = numpy.empty((size,), dtype=numpy.float32)
    gt_array = numpy.empty((size,), dtype=numpy.bool_)
    for i, sample in enumerate(tqdm(predictions, desc="sample")):
        with h5py.File(prediction_path / sample[1], "r") as f:
            mask = numpy.array(f["mask"])  # boolean
            pred = numpy.array(f["prediction"])  # float32
            pred *= mask.astype(numpy.float32)
            gt = numpy.array(f["target"])  # boolean
            gt &= mask
            pred_array[i * elements : (i + 1) * elements] = pred.flatten()
            gt_array[i * elements : (i + 1) * elements] = gt.flatten()

    return pred_array, gt_array


def compute_metric(
    counts: numpy.typing.NDArray[numpy.uint64],
    metric: typing.Callable[[int, int, int, int], float]
    | typing.Callable[[int, int, int, int], tuple[float, ...]],
) -> numpy.typing.NDArray[numpy.float64]:
    """Compute ``metric`` for every row of ``counts``.

    Parameters
    ----------
    counts
        A 2-D array with shape ``(*, 4)``, where each row contains to the
        counts of true positives, false positives, true negatives and false
        negatives, that need to be evaluated.
    metric
        A callable that takes 4 integers representing true positives, false
        positives, true negatives and false negatives, and outputs one or more
        floating-point metrics.

    Returns
    -------
        An 1-D array containing the provided metric computed alongside the
        first dimension and as many columns as ```metric`` provides in each
        call.
    """
    return numpy.array([metric(*k) for k in counts], dtype=numpy.float64)


def validate_threshold(threshold: float | str, splits: list[str]):
    """Validate the user threshold selection and returns parsed threshold.

    Parameters
    ----------
    threshold
        The threshold to validate.
    splits
        List of available splits.

    Returns
    -------
        The validated threshold.
    """
    try:
        # we try to convert it to float first
        threshold = float(threshold)
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("Float thresholds must be within range [0.0, 1.0]")
    except ValueError:
        if threshold not in splits:
            raise ValueError(
                f"Text thresholds should match dataset names, "
                f"but {threshold} is not available among the datasets provided ("
                f"({', '.join(splits)})"
            )

    return threshold


def compare_annotators(
    a1: pathlib.Path, a2: pathlib.Path
) -> dict[str, dict[str, float]]:
    """Compare annotators and outputs all supported metrics.

    Parameters
    ----------
    a1
        Annotator 1 annotations in the form of a JSON file mapping split-names
        ot list of lists, each containing the sample name and the (relative)
        location of an HDF5 file containing at least one boolean dataset named
        ``target``.  This dataset is considered as the annotations from the
        first annotator.  If a boolean ``mask`` is available, it is also
        loaded.  All elements outside the mask are not considered during the
        metrics calculations.
    a2
        Annotator 1 annotations in the form of a JSON file mapping split-names
        ot list of lists, each containing the sample name and the (relative)
        location of an HDF5 file containing at least one boolean dataset named
        ``target``.  This dataset is considered as the annotations from the
        second annotator.

    Returns
    -------
        A dictionary that maps split-names to another dictionary with metric
        names and values computed by comparing the targets in ``a1`` and
        ``a2``.
    """

    retval: dict[str, dict[str, float]] = {}

    with a1.open("r") as f:
        a1_data = json.load(f)

    with a2.open("r") as f:
        a2_data = json.load(f)

    metrics_available = list(typing.get_args(SUPPORTED_METRIC_TYPE))

    for split_name, samples in a1_data.items():
        if split_name not in a2_data:
            continue

        for _, hdf5_path in samples:
            with h5py.File(a1.parent / hdf5_path, "r") as f:
                t1 = numpy.array(f["target"])
                mask = numpy.array(f["mask"])
            with h5py.File(a2.parent / hdf5_path, "r") as f:
                t2 = numpy.array(f["target"])

            tp, fp, tn, fn = get_counts_for_threshold(t2, t1, mask, 0.5)
            base_metrics = all_metrics(tp, fp, tn, fn)
            retval[split_name] = {k: v for k, v in zip(metrics_available, base_metrics)}

    return retval


def run(
    predictions: pathlib.Path,
    steps: int,
    threshold: str | float,
    metric: SUPPORTED_METRIC_TYPE,
) -> tuple[dict[str, dict[str, typing.Any]], float]:
    """Evaluate a segmentation model.

    Parameters
    ----------
    predictions
        Path to the file ``predictions.json``, containing the list of
        predictions to be evaluated.
    steps
        The number of steps between ``[0, 1]`` to build a threshold list
        from.  This list will be applied to the probability outputs and
        true/false positive/negative counts generated from those.
    threshold
        Which threshold to apply when generating unary summaries of the
        performance.  This can be a value between ``[0, 1]``, or the name
        of a split in ``predictions`` where a threshold will be calculated
        at.
    metric
        The name of a supported metric that will be used to evaluate the
        best threshold from a threshold-list uniformily split in ``steps``,
        and for which unary summaries are generated.

    Returns
    -------
        A JSON-able summary with all figures of merit pre-caculated, for
        all splits.  This is a dictionary where keys are split-names contained
        in ``predictions``, and values are dictionaries with the following
        keys:

            * ``counts``: dictionary where keys are thresholds, and values are
              sequence of integers containing the TP, FP, TN, FN (in this order).

            * ``roc_auc``: a float indicating the area under the ROC curve
              for the split.  It is calculated using a trapezoidal rule.

            * ``average_precision``: a float indicating the area under the
              precision-recall curve, calculated using a rectangle rule.

            * ``curves``: dictionary with 2 keys:

              * ``roc``: dictionary with 3 keys:

                * ``fpr``: a list of floats with the false-positive rate
                * ``tpr``: a list of floats with the true-positive rate
                * ``thresholds``: a list of thresholds uniformily separated by
                  ``steps``, at which both ``fpr`` and ``tpr`` are evaluated.
              * ``precision_recall``: a dictionary with 3 keys:

                * ``precision``: a list of floats with the precision
                * ``recall``: a list of floats with the recall
                * ``thresholds``: a list of thresholds uniformily separated by
                  ``steps``, at which both ``precision`` and ``recall`` are
                  evaluated.

            * ``threshold_a_priori``: boolean indicating if the threshold for unary
              metrics where computed with a threshold chosen a priori or a
              posteriori in this split.

            * ``<metric-name>``: a float representing the supported metric at the
              threshold that maximizes ``metric``.  There will be one entry of this
              type for each of the :py:obj:`SUPPORTED_METRIC_TYPE`'s.

        Also returns the threshold considered for all splits.
    """

    with predictions.open("r") as f:
        predict_data = json.load(f)

    threshold = validate_threshold(threshold, predict_data)
    threshold_list = numpy.arange(
        0.0, (1.0 + 1 / steps), 1 / steps, dtype=numpy.float64
    )

    # Holds all computed data.  Format <split-name: str> -> <split-data: dict>
    eval_json_data: dict[str, dict[str, typing.Any]] = {}

    # Compute counts for various splits.
    for split_name, samples in predict_data.items():
        logger.info(
            f"Counting true/false positive/negatives at split `{split_name}`..."
        )
        counts = load_count(predictions.parent, samples, threshold_list)

        logger.info(f"Evaluating performance curves/metrics at split `{split_name}`...")
        fpr_curve = 1.0 - numpy.array([specificity(*k) for k in counts])
        recall_curve = tpr_curve = numpy.array([recall(*k) for k in counts])
        precision_curve = numpy.array([precision(*k) for k in counts])

        # correction when precision is very small
        precision_curve[
            numpy.logical_and(precision_curve < 1e-8, recall_curve < 1e-8)
        ] = 1.0

        # populates data to be recorded in JSON format
        eval_json_data.setdefault(split_name, {})["samples"] = len(samples)
        eval_json_data.setdefault(split_name, {})["counts"] = {
            k: v for k, v in zip(threshold_list, counts)
        }
        eval_json_data.setdefault(split_name, {})["roc_auc"] = (
            credible.curves.area_under_the_curve((fpr_curve, tpr_curve))
        )
        eval_json_data.setdefault(split_name, {})["average_precision"] = (
            credible.curves.average_metric((precision_curve, recall_curve))
        )
        eval_json_data.setdefault(split_name, {})["curves"] = dict(
            roc=dict(fpr=fpr_curve, tpr=tpr_curve, thresholds=threshold_list),
            precision_recall=dict(
                precision=precision_curve,
                recall=recall_curve,
                thresholds=threshold_list,
            ),
        )

    # Computes argmax in the designated split "counts" (typically "validation"),
    # where the chosen metric reaches its **maximum**.
    if isinstance(threshold, str):
        # Compute threshold on specified split, if required
        logger.info(f"Evaluating threshold on split `{threshold}` using " f"`{metric}`")
        metric_list = compute_metric(
            eval_json_data[threshold]["counts"].values(),
            name2metric(typing.cast(SUPPORTED_METRIC_TYPE, metric)),
        )
        threshold_index = metric_list.argmax()

        # Reset list of how thresholds are calculated on the recorded split
        for split_name in predict_data.keys():
            if split_name == threshold:
                eval_json_data[split_name]["threshold_a_priori"] = False
            else:
                eval_json_data[split_name]["threshold_a_posteriori"] = True

    else:
        # must figure out the closest threshold from the list we are using
        threshold_index = (numpy.abs(threshold_list - threshold)).argmin()

        # Reset list of how thresholds are calculated on the recorded split
        for split_name in predict_data.keys():
            eval_json_data[split_name]["threshold_a_priori"] = True

    logger.info(f"Set --threshold={threshold_list[threshold_index]:.4f}")

    # Computes all available metrics on the designated threshold, across all
    # splits
    # Populates <split-name: str> -> <metric-name: SUPPORTED_METRIC_TYPE> ->
    # float
    metrics_available = list(typing.get_args(SUPPORTED_METRIC_TYPE))
    for split_name in predict_data.keys():
        logger.info(
            f"Computing metrics on split `{split_name}` at "
            f"threshold={threshold_list[threshold_index]:.4f}..."
        )
        base_metrics = all_metrics(
            *(list(eval_json_data[split_name]["counts"].values())[threshold_index])
        )
        eval_json_data[split_name]["threshold"] = threshold_list[threshold_index]
        eval_json_data[split_name].update(
            {k: v for k, v in zip(metrics_available, base_metrics)}
        )

    return eval_json_data, threshold_list[threshold_index]


def make_table(
    eval_data: dict[str, dict[str, typing.Any]], threshold: float, format_: str
) -> str:
    """Extract and format table from pre-computed evaluation data.

    Extracts elements from ``eval_data`` that can be displayed on a
    terminal-style table, format, and returns it.

    Parameters
    ----------
    eval_data
        Evaluation data as returned by :py:func:`run`.
    threshold
        The threshold value used to compute unary metrics on all splits.
    format_
        A supported tabulate format.

    Returns
    -------
        A string representation of a table.
    """

    # Extracts elements from ``eval_json_data`` that can be displayed on a
    # terminal-style table, format, and print to screen.  Record the table into
    # a file for later usage.
    metrics_available = list(typing.get_args(SUPPORTED_METRIC_TYPE))
    table_headers = (
        ["subset", "samples", "threshold"] + metrics_available + ["auc_roc", "avg.prec"]
    )

    table_data = []
    for split_name, data in eval_data.items():
        base_metrics = [data[k] for k in metrics_available]
        table_data.append(
            [split_name, data["samples"], threshold]
            + base_metrics
            + [data["roc_auc"], data["average_precision"]]
        )

        if "second_annotator" in data:
            table_data.append(
                [split_name, "annotator/2"]
                + list(data["second_annotator"].values())
                + [None, None]
            )

    return tabulate.tabulate(
        table_data,
        table_headers,
        tablefmt=format_,
        floatfmt=".3f",
        stralign="right",
    )


def make_plots(eval_data: dict[str, dict[str, typing.Any]]) -> list:
    """Create plots for all curves in ``eval_data``.

    Parameters
    ----------
    eval_data
        Evaluation data as returned by :py:func:`run`.

    Returns
    -------
        A list of figures to record to file
    """
    retval = []

    with credible.plot.tight_layout(
        ("False Positive Rate", "True Positive Rate"), "ROC"
    ) as (fig, ax):
        for split_name, data in eval_data.items():
            ax.plot(
                data["curves"]["roc"]["fpr"],
                data["curves"]["roc"]["tpr"],
                label=f"{split_name} (AUC: {data['roc_auc']:.2f})",
            )

            if "second_annotator" in data:
                fpr = 1 - data["second_annotator"]["specificity"]
                tpr = data["second_annotator"]["recall"]
                ax.plot(
                    fpr,
                    tpr,
                    linestyle="none",
                    marker="*",
                    markersize=8,
                    label=f"{split_name} (annotator/2)",
                )

            ax.legend(loc="best", fancybox=True, framealpha=0.7)
        retval.append(fig)

    with credible.plot.tight_layout_f1iso(
        ("Recall", "Precision"), "Precison-Recall"
    ) as (fig, ax):
        for split_name, data in eval_data.items():
            ax.plot(
                data["curves"]["precision_recall"]["recall"],
                data["curves"]["precision_recall"]["precision"],
                label=f"{split_name} (AP: {data['average_precision']:.2f})",
            )

            if "second_annotator" in data:
                recall = data["second_annotator"]["recall"]
                precision = data["second_annotator"]["precision"]
                ax.plot(
                    recall,
                    precision,
                    linestyle="none",
                    marker="*",
                    markersize=8,
                    label=f"{split_name} (annotator/2)",
                )

            ax.legend(loc="best", fancybox=True, framealpha=0.7)
        retval.append(fig)

    return retval
