# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import h5py
import numpy
import numpy.typing
import PIL.Image
import PIL.ImageOps
import torch
import torchvision.transforms.v2.functional

from .evaluator import tfpn_masks


def view(
    basedir: pathlib.Path,
    stem: str,
    threshold: float,
    show_errors: bool,
    tp_color: tuple[int, int, int],
    fp_color: tuple[int, int, int],
    fn_color: tuple[int, int, int],
    alpha: float,
) -> PIL.Image.Image:
    """Create an segmentation map visualisation.

    Parameters
    ----------
    basedir
        Base directory where the prediction indicated by ``stem`` is stored.
    stem
        Name of the HDF5 file containing the predictions, as output by the
        ``predict`` CLI.
    threshold
        The threshold to apply to the probability map loaded from the HDF5
        file.
    show_errors
        If set to ``True``, then colours false-positives (in red), and false
        negatives (in green).
    tp_color
        Tuple that indicates which color to use for displaying true-positives.
    fp_color
        Tuple that indicates which color to use for displaying false-positives.
    fn_color
        Tuple that indicates which color to use for displaying false-negatives.
    alpha
        How transparent will the overlay be.

    Returns
    -------
        An image with an overlayed segmentation map that can be saved or
        displayed.
    """

    def _to_pil(arr: numpy.typing.NDArray[numpy.float32]) -> PIL.Image.Image:
        return torchvision.transforms.v2.functional.to_pil_image(torch.Tensor(arr))

    with h5py.File(basedir / stem, "r") as f:
        image: numpy.typing.NDArray[numpy.float32] = numpy.array(f["image"])
        target: numpy.typing.NDArray[numpy.bool_] = numpy.array(f["target"])
        mask: numpy.typing.NDArray[numpy.bool_] = numpy.array(f["mask"])

        pred: numpy.typing.NDArray[numpy.float32] = numpy.empty(
            (0,), dtype=numpy.float32
        )
        if "prediction" in f:
            pred = numpy.array(f["prediction"])

    image *= mask
    target = numpy.logical_and(target, mask)

    if pred.shape == (0,):
        # no prediction available, can only show target

        image *= mask
        target = numpy.logical_and(target, mask)

        overlay = target >= 0.5
        tp_pil = _to_pil(overlay.astype(numpy.float32))
        tp_pil_colored = PIL.ImageOps.colorize(tp_pil, (0, 0, 0), tp_color)

        retval = _to_pil(image)
        return PIL.Image.blend(retval, tp_pil_colored, alpha)

    # there is a prediction - show more information
    pred *= mask
    if show_errors:
        tp, fp, _, fn = tfpn_masks(pred, target, threshold)

        # change to PIL representation
        tp_pil = _to_pil(tp.astype(numpy.float32))
        tp_pil_colored = PIL.ImageOps.colorize(tp_pil, (0, 0, 0), tp_color)

        fp_pil = _to_pil(fp.astype(numpy.float32))
        fp_pil_colored = PIL.ImageOps.colorize(fp_pil, (0, 0, 0), fp_color)

        fn_pil = _to_pil(fn.astype(numpy.float32))
        fn_pil_colored = PIL.ImageOps.colorize(fn_pil, (0, 0, 0), fn_color)

        tp_pil_colored.paste(fp_pil_colored, mask=fp_pil)
        tp_pil_colored.paste(fn_pil_colored, mask=fn_pil)

    else:
        overlay = pred >= threshold
        tp_pil = _to_pil(overlay.astype(numpy.float32))
        tp_pil_colored = PIL.ImageOps.colorize(tp_pil, (0, 0, 0), tp_color)

    retval = _to_pil(image)
    return PIL.Image.blend(retval, tp_pil_colored, alpha)
