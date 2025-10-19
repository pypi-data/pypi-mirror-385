# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Image transformations for our pipelines.

Differences between methods here and those from
:py:mod:`torchvision.transforms` is that these support multiple
simultaneous image inputs, which are required to feed segmentation
networks (e.g. image and labels or masks).  We also take care of data
augmentations, in which random flipping and rotation needs to be applied
across all input images, but color jittering, for example, only on the
input image.
"""

import functools
import logging
import typing

import numpy.random
import numpy.typing
import torch
from scipy.ndimage import gaussian_filter, map_coordinates

logger = logging.getLogger(__name__)


def _elastic_deformation_on_image(
    img: torch.Tensor,
    rng: numpy.random.Generator,
    alpha: float = 1000.0,
    sigma: float = 30.0,
    spline_order: int = 1,
    mode: str = "nearest",
    p: float = 1.0,
) -> torch.Tensor:
    """Perform elastic deformation on an image.

    This implementation is based on 2 scipy functions
    (:py:func:`scipy.ndimage.gaussian_filter` and
    :py:func:`scipy.ndimage.map_coordinates`).  It is very inefficient since it
    requires data to be moved off the current running device and then back.

    Parameters
    ----------
    img
        The input image to apply elastic deformation to.  This image should
        always have this shape: ``[C, H, W]``. It should always represent a
        tensor on the CPU.
    rng
        The numpy random number generator to use.
    alpha
        A multiplier for the gaussian filter outputs.
    sigma
        Standard deviation for Gaussian kernel.
    spline_order
        The order of the spline interpolation, default is 1. The order has to
        be in the range 0-5.
    mode
        The mode parameter determines how the input array is extended beyond
        its boundaries.
    p
        Probability that this transformation will be applied.  Meaningful when
        using it as a data augmentation technique.

    Returns
    -------
    tensor
        The image with elastic deformation applied, as a tensor on the CPU.
    """

    if rng.random() < p:
        assert img.ndim == 3, (
            f"This filter accepts only images with 3 dimensions, "
            f"however I got an image with {img.ndim} dimensions."
        )

        # Input tensor is of shape C x H x W
        img_shape = img.shape[1:]

        dx = alpha * typing.cast(
            numpy.typing.NDArray[numpy.float64],
            gaussian_filter(
                (rng.random(size=(img_shape[0], img_shape[1])) * 2 - 1),
                sigma,
                mode="constant",
                cval=0.0,
            ),
        )
        dy = alpha * typing.cast(
            numpy.typing.NDArray[numpy.float64],
            gaussian_filter(
                (rng.random(size=(img_shape[0], img_shape[1])) * 2 - 1),
                sigma,
                mode="constant",
                cval=0.0,
            ),
        )

        x, y = numpy.meshgrid(
            numpy.arange(img_shape[0]),
            numpy.arange(img_shape[1]),
            indexing="ij",
        )
        indices = [
            numpy.reshape(x + dx, (-1, 1)),
            numpy.reshape(y + dy, (-1, 1)),
        ]

        # may copy, if img is not on CPU originally
        img_numpy = img.numpy()
        output = numpy.zeros_like(img_numpy)
        for i in range(img.shape[0]):
            output[i, :, :] = torch.tensor(
                map_coordinates(
                    img_numpy[i, :, :],
                    indices,
                    order=spline_order,
                    mode=mode,
                ).reshape(img_shape),
            )

        # wraps numpy array as tensor, move to destination device if need-be
        return torch.as_tensor(output)

    return img


def _elastic_deformation_on_batch(
    batch: torch.Tensor,
    rng: numpy.random.Generator,
    alpha: float = 1000.0,
    sigma: float = 30.0,
    spline_order: int = 1,
    mode: str = "nearest",
    p: float = 1.0,
) -> torch.Tensor:
    """Perform elastic deformation on a batch of images.

    This implementation is based on 2 scipy functions
    (:py:func:`scipy.ndimage.gaussian_filter` and
    :py:func:`scipy.ndimage.map_coordinates`).  It is very inefficient since it
    requires data to be moved off the current running device and then back.

    Parameters
    ----------
    batch
        The batch to apply elastic deformation to.
    rng
        The numpy random number generator to use.
    alpha
        A multiplier for the gaussian filter outputs.
    sigma
        Standard deviation for Gaussian kernel.
    spline_order
        The order of the spline interpolation, default is 1. The order has to
        be in the range 0-5.
    mode
        The mode parameter determines how the input array is extended beyond
        its boundaries.
    p
        Probability that this transformation will be applied.  Meaningful when
        using it as a data augmentation technique.

    Returns
    -------
    tensor
        A batch of images with elastic deformation applied, as a tensor on the CPU.
    """

    # transforms our custom functions into simpler callables
    partial = functools.partial(
        _elastic_deformation_on_image,
        rng=rng,
        alpha=alpha,
        sigma=sigma,
        spline_order=spline_order,
        mode=mode,
        p=p,
    )

    # if a mp pool is available, do it in parallel
    augmented_images: typing.Any
    augmented_images = map(partial, batch.cpu())
    return torch.stack(list(augmented_images))


class ElasticDeformation:
    """Elastic deformation of 2D image slightly adapted from :cite:p:`simard_best_2003`.

    This implementation is based on 2 scipy functions
    (:py:func:`scipy.ndimage.gaussian_filter` and
    :py:func:`scipy.ndimage.map_coordinates`).  It is very inefficient since it
    requires data to be moved off the current running device and then back.

    .. warning::

       Furthermore, this transform is not scriptable and therefore cannot run
       on a CUDA or MPS device.  Applying it effectively creates a bottleneck
       in model training.

    Source: https://gist.github.com/oeway/2e3b989e0343f0884388ed7ed82eb3b0

    Parameters
    ----------
    alpha
        A multiplier for the gaussian filter outputs.
    sigma
        Standard deviation for Gaussian kernel.
    spline_order
        The order of the spline interpolation, default is 1. The order has to
        be in the range 0-5.
    mode
        The mode parameter determines how the input array is extended beyond
        its boundaries.
    p
        Probability that this transformation will be applied.  Meaningful when
        using it as a data augmentation technique.
    seed
        Set the random generator seed, if given.  Otherwise, initializes the generator
        with a random seed (c.f. :py:func:`numpy.random.default_rng`).
    """

    def __init__(
        self,
        alpha: float = 1000.0,
        sigma: float = 30.0,
        spline_order: int = 1,
        mode: str = "nearest",
        p: float = 1.0,
        seed: int | None = None,
    ):
        self.alpha: float = alpha
        self.sigma: float = sigma
        self.spline_order: int = spline_order
        self.mode: str = mode
        self.p: float = p
        self.seed = seed
        self.npy_rng = numpy.random.default_rng(seed=seed)

    def __str__(self) -> str:
        parameters = [
            f"alpha={self.alpha}",
            f"sigma={self.sigma}",
            f"spline_order={self.spline_order}",
            f"mode={self.mode}",
            f"p={self.p}",
            f"seed={self.seed}",
        ]
        return f"{type(self).__name__}({', '.join(parameters)})"

    def __call__(self, img: torch.Tensor) -> torch.Tensor:
        if len(img.shape) == 4:
            return _elastic_deformation_on_batch(
                batch=img,
                rng=self.npy_rng,
                alpha=self.alpha,
                sigma=self.sigma,
                spline_order=self.spline_order,
                mode=self.mode,
                p=self.p,
            ).to(img.device)

        if len(img.shape) == 3:
            return _elastic_deformation_on_image(
                img=img.cpu(),
                rng=self.npy_rng,
                alpha=self.alpha,
                sigma=self.sigma,
                spline_order=self.spline_order,
                mode=self.mode,
                p=self.p,
            ).to(img.device)

        raise RuntimeError(
            f"This transform accepts only images with 3 dimensions,"
            f"or batches of images with 4 dimensions.  However, I got "
            f"an image with {img.ndim} dimensions.",
        )
