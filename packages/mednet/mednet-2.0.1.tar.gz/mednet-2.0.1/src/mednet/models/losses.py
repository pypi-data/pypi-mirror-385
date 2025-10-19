# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Custom losses for different tasks."""

import logging
import typing

import numpy.typing
import torch
import torch.utils.data

from ..data.datamodule import ConcatDataModule
from ..data.typing import Dataset
from .typing import TaskType

logger = logging.getLogger(__name__)


def _task_type(
    targets: torch.Tensor
    | numpy.typing.NDArray
    | typing.Iterable[typing.Iterable[int]]
    | typing.Iterable[typing.Iterable[typing.Iterable[typing.Iterable[int]]]],
) -> TaskType:
    """Determine the type of task from combined targets available.

    This function will look into the provided targets of a dataset and will
    determine the type of task.

    Parameters
    ----------
    targets
        The complete target set, for the whole dataset being analyzed. This
        matrix should be ``[n, C]`` where ``n`` is the number of samples, and
        ``C`` the number of classes.  All values should be either 0 or 1.

    Returns
    -------
        The type of tas
    """

    int_targets = torch.Tensor(targets).int()

    task_type: TaskType = "classification"
    if len(int_targets.shape) > 2:
        task_type = "segmentation"

    return task_type


def _get_positive_weights_from_targets(targets: torch.Tensor) -> torch.Tensor:
    """Compute the weights of each class of a set of targets.

    This function inputs a set of targets and computes the ratio between number
    of negative and positive samples (scalar).  The weight can be used to
    adjust minimisation criteria to in cases there is a huge data imbalance.

    It returns a vector with weights (inverse counts) for each target.

    Parameters
    ----------
    targets
        A :py:class:`torch.Tensor` containing the targets, in the format
        ``[n, C]`` where ``n`` is the number of samples and ``C`` the
        number of classes.

    Returns
    -------
        The positive weight of each class in the dataset given as input.
    """

    task_type = _task_type(targets)

    if task_type == "segmentation":
        # rearranges ``targets`` vector so the problem looks like a simpler
        # classification problem where each pixel is a "separate sample"
        targets = targets.transpose(0, 2).transpose(1, 3).reshape(-1, targets.shape[1])

    positive_count = targets.sum(dim=0)
    negative_count = targets.shape[0] - positive_count
    return negative_count / positive_count


def _get_positive_weights_from_dataloader(
    dataloader: torch.utils.data.DataLoader,
) -> torch.Tensor:
    """Compute the weights of each class of a DataLoader.

    This function inputs a :py:class:`torch.utils.data.DataLoader` and computes
    the ratio between number of negative and positive samples (scalar).  The
    weight can be used to adjust minimisation criteria to in cases there is a
    huge data imbalance.

    It returns a vector with weights (inverse counts) for each target.

    Parameters
    ----------
    dataloader
        A DataLoader from which to compute the positive weights.  Entries must
        be a dictionary which must contain a ``target`` key.

    Returns
    -------
        The positive weight of each class in the dataset given as input.

    Raises
    ------
    NotImplementedError
        In the case of "multilabel" datasets, which are currently not
        supported.
    """

    if isinstance(dataloader.dataset, Dataset):
        # there is a faster way to access the targets!
        targets = dataloader.dataset.targets()
    else:
        targets = [batch["target"] for batch in dataloader]

    return _get_positive_weights_from_targets(torch.vstack(targets))


def pos_weight_for_bcewithlogitsloss(
    datamodule: ConcatDataModule,
) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    """Generate the ``pos_weight`` argument for losses of type :py:class:`torch.nn.BCEWithLogitsLoss`.

    This function can generate the ``pos_weight`` parameters for both train and
    validation losses given a datamodule.

    Parameters
    ----------
    datamodule
        The datamodule to probe for training and validation datasets.

    Returns
    -------
        A tuple containing the training and validation ``pos_weight``
        arguments, wrapped in a dictionary.
    """

    train_weights = _get_positive_weights_from_dataloader(
        datamodule.unshuffled_train_dataloader()
    )
    logger.info(f"train: BCEWithLogitsLoss(pos_weight={train_weights})")

    if "validation" in datamodule.val_dataloader().keys():
        validation_weights = _get_positive_weights_from_dataloader(
            datamodule.val_dataloader()["validation"]
        )
    else:
        logger.warning(
            "Datamodule does not contain a validation dataloader. "
            "The training dataloader will be used instead."
        )
        validation_weights = train_weights
    logger.info(f"validation: BCEWithLogitsLoss(weight={validation_weights})")

    return (dict(pos_weight=train_weights), dict(pos_weight=validation_weights))


class BCEWithLogitsLossWeightedPerBatch(torch.nn.Module):
    """Calculates the binary cross entropy loss for every batch.

    This loss is similar to :py:class:`torch.nn.BCEWithLogitsLoss`, except it
    updates the ``pos_weight`` (ratio between negative and positive target
    pixels) parameter for the loss term for every batch, based on the
    accumulated taget pixels for all samples in the batch.

    Implements Equation 1 in :cite:p:`maninis_deep_2016`.  The weight depends on the
    current proportion between negatives and positives in the ground-
    truth sample being analyzed.
    """

    def __init__(self):
        super().__init__()

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Logits produced by the model to be evaluated, with the shape ``[n,
            c]`` (classification), or ``[n, c, h, w]`` (segmentation).
        target
            Ground-truth information with the shape  ``[n, c]``
            (classification), or ``[n, c, h, w]`` (segmentation), containing
            zeroes and ones.

        Returns
        -------
            The average loss for all input data.
        """

        # calculates the proportion of negatives to the total number of pixels
        # available in the masked region
        num_pos = target.sum()
        return torch.nn.functional.binary_cross_entropy_with_logits(
            input_,
            target,
            reduction="mean",
            pos_weight=(input_.numel() - num_pos) / num_pos,
        )


class SoftJaccardAndBCEWithLogitsLoss(torch.nn.Module):
    r"""Implement the generalized loss function of Equation (3) at :cite:p:`iglovikov_ternausnetv2_2018`.

    At the paper, authors suggest a value of :math:`\alpha = 0.7`, which we set
    as default for instances of this type.

    .. math::

       L = \alpha H + (1-\alpha)(1-J)

    J is the Jaccard distance, and H, the Binary Cross-Entropy Loss.  Our
    implementation is based on :py:class:`torch.nn.BCEWithLogitsLoss`.

    Parameters
    ----------
    alpha
        Determines the weighting of J and H. Default: ``0.7``.
    """

    def __init__(self, alpha: float = 0.7):
        super().__init__()
        self.alpha = alpha

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Logits produced by the model to be evaluated, with the shape ``[n,
            c]`` (classification), or ``[n, c, h, w]`` (segmentation).
        target
            Ground-truth information with the shape  ``[n, c]``
            (classification), or ``[n, c, h, w]`` (segmentation), containing
            zeroes and ones.

        Returns
        -------
            Loss, in a single entry.
        """

        eps = 1e-8
        probabilities = torch.sigmoid(input_)
        intersection = (probabilities * target).sum()
        sums = probabilities.sum() + target.sum()
        j = intersection / (sums - intersection + eps)

        # this implements the support for looking just into the RoI
        h = torch.nn.functional.binary_cross_entropy_with_logits(
            input_, target, reduction="mean"
        )
        return (self.alpha * h) + ((1 - self.alpha) * (1 - j))


class MultiLayerBCELogitsLossWeightedPerBatch(BCEWithLogitsLossWeightedPerBatch):
    """Weighted Binary Cross-Entropy Loss for multi-layered inputs.

    This loss can be used in networks that produce more than one output that
    has to match output targets.  For example, architectures such as
    as :py:class:`.hed.HED` or :py:class:`.lwnet.LittleWNet` require this
    feature.

    It follows the inherited super class applying on-the-fly `pos_weight`
    updates per batch.
    """

    def __init__(self):
        super().__init__()

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Logits produced by the model to be evaluated, with the shape ``[n,
            c]`` (classification), or ``[n, c, h, w]`` (segmentation).
        target
            Ground-truth information with the shape  ``[n, c]``
            (classification), or ``[n, c, h, w]`` (segmentation), containing
            zeroes and ones.

        Returns
        -------
            The average loss for all input data.
        """

        fwd = super().forward
        return torch.cat([fwd(i, target).unsqueeze(0) for i in input_]).mean()


class MultiLayerSoftJaccardAndBCELogitsLoss(SoftJaccardAndBCEWithLogitsLoss):
    """Implement Equation 3 in :cite:p:`iglovikov_ternausnetv2_2018` for the multi-output networks.

    This loss can be used in networks that produce more than one output that
    has to match output targets.  For example, architectures such as
    as :py:class:`.hed.HED` or :py:class:`.lwnet.LittleWNet` require this
    feature.

    Parameters
    ----------
    alpha : float
        Determines the weighting of SoftJaccard and BCE. Default: ``0.7``.
    """

    def __init__(self, alpha: float = 0.7):
        super().__init__(alpha=alpha)

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Logits produced by the model to be evaluated, with the shape ``[n,
            c]`` (classification), or ``[n, c, h, w]`` (segmentation).
        target
            Ground-truth information with the shape  ``[n, c]``
            (classification), or ``[n, c, h, w]`` (segmentation), containing
            zeroes and ones.

        Returns
        -------
            The average loss for all input data.
        """

        fwd = super().forward
        return torch.cat([fwd(i, target).unsqueeze(0) for i in input_]).mean()


class MOONBCEWithLogitsLoss(torch.nn.Module):
    """Calculates the weighted binary cross entropy loss based on :cite:p:`guler_refining_2024`.

    This loss implements the domain-adapted multitask loss function in Equation
    (2) on :cite:p:`guler_refining_2024`.  The vector of input weights must be calculated from
    the input dataset in advance, and set during initialization, or later,
    before the loss can be fully used.

    Parameters
    ----------
    weights
        The positive weight of each class in the dataset given as input as a
        ``[2, C]`` tensor, with :math:`w_i^-` at position 0, and :math:`w_i^+`
        at position 1, as defined in Equation (1) of :cite:p:`guler_refining_2024`.
    """

    def __init__(self, weights: torch.Tensor | None = None):
        super().__init__()
        self.weights = weights

    @classmethod
    def _get_weight_from_targets(cls, targets: torch.Tensor) -> torch.Tensor:
        r"""Compute the MOON weights from a set of targets as per Equation
        (1) in :cite:p:`guler_refining_2024`.

        Parameters
        ----------
        targets
            A :py:class:`torch.Tensor` containing the targets, in the format
            ``[n, C]`` where ``n`` is the number of samples and ``C`` the
            number of classes.

        Returns
        -------
            The weight of each class in the dataset given as input as a ``[2,
            C]`` tensor, with :math:`w_i^-` at position 0, and :math:`w_i^+` at
            position 1, as defined in Equation (1) of :cite:p:`guler_refining_2024`.
        """

        task_type = _task_type(targets)

        if task_type == "segmentation":
            # rearranges ``targets`` vector so the problem looks like a simpler
            # classification problem where each pixel is a "separate sample"
            targets = (
                targets.transpose(0, 2).transpose(1, 3).reshape(-1, targets.shape[1])
            )

        # at this point targets should be [n x C]
        s_plus = targets.sum(dim=0)
        s_minus = targets.shape[0] - s_plus
        w_minus = (s_plus / s_minus).clamp(min=0, max=1)
        w_plus = (s_minus / s_plus).clamp(min=0, max=1)

        return torch.vstack((w_minus, w_plus))

    @classmethod
    def _get_weight_from_dataloader(
        cls, dataloader: torch.utils.data.DataLoader
    ) -> torch.Tensor:
        r"""Compute the MOON weights of each class of a DataLoader as per Equation
        (1) in :cite:p:`guler_refining_2024`.

        Parameters
        ----------
        dataloader
            A DataLoader from which to compute the positive weights.  Entries must
            be a dictionary which must contain a ``target`` key.

        Returns
        -------
            The weight of each class in the dataset given as input as a ``[2,
            C]`` tensor, with :math:`w_i^-` at position 0, and :math:`w_i^+` at
            position 1, as defined in Equation (1) of :cite:p:`guler_refining_2024`.
        """

        if isinstance(dataloader.dataset, Dataset):
            # there is a faster way to access the targets!
            targets = dataloader.dataset.targets()
        else:
            targets = [batch["target"] for batch in dataloader]

        return cls._get_weight_from_targets(torch.vstack(targets))

    @classmethod
    def get_arguments_from_datamodule(
        cls, datamodule: ConcatDataModule
    ) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
        r"""Compute the MOON weights for train and validation sets of a datamodule.

        This function inputs a :py:class:`.data.datamodule.ConcatDataModule`,
        and for both the training and validation sets, and for each class on
        the respective dataloader targets, computes negative and positive
        weights as such:

        .. math::

           \begin{align}
               w_i^+ &=
                   \begin{cases}
                       1 & \text{if } S^{-}_{i} > S^{+}_{i} \\
                       \frac{S^{-}_{i}}{S^{+}_{i}} & \text{otherwise}
                   \end{cases} &
               w_i^- &=
                   \begin{cases}
                       1 & \text{if } S^{+}_{i} > S^{-}_{i} \\
                       \frac{S^{+}_{i}}{S^{-}_{i}} & \text{otherwise}
                   \end{cases}
           \end{align}

        This weight vector is used during runtime to balance individual batch
        losses respecting individual class distributions.

        Parameters
        ----------
        datamodule
            The datamodule to probe for training and validation datasets.

        Returns
        -------
            A tuple containing the training and validation ``weight``
            arguments, wrapped in a dictionary. Each ``weight`` variable
            contains the weights of each class in the target dataset as a ``[2,
            C]`` tensor, with :math:`w_i^-` at position 0, and :math:`w_i^+` at
            position 1, as defined in Equation (1) of :cite:p:`guler_refining_2024`.
        """

        train_weights = cls._get_weight_from_dataloader(
            datamodule.unshuffled_train_dataloader()
        )
        logger.info(f"train: MOONBCEWithLogitsLoss(weight={train_weights})")

        if "validation" in datamodule.val_dataloader().keys():
            validation_weights = cls._get_weight_from_dataloader(
                datamodule.val_dataloader()["validation"]
            )
        else:
            logger.warning(
                "Datamodule does not contain a validation dataloader. "
                "The training dataloader will be used instead."
            )
            validation_weights = train_weights
        logger.info(f"validation: MOONBCEWithLogitsLoss(weight={validation_weights})")

        return (dict(weights=train_weights), dict(weights=validation_weights))

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        r"""Forward pass.

        This function inputs the output of the model and a set of binary
        targets (as a float tensor containing zeroes and ones), and implements
        Equation (2) from :cite:p:`guler_refining_2024`:

        .. math::

           \mathcal J = -\sum_{i=1}^M w_i^{t_i} \bigl[t_i\log f_i(x) +
           (1-t_i)\log (1-f_i(x)) \bigr]

        Parameters
        ----------
        input_
            Logits produced by the model to be evaluated, with the shape ``[n,
            c]`` (classification), or ``[n, c, h, w]`` (segmentation).
        target
            Ground-truth information with the shape  ``[n, c]``
            (classification), or ``[n, c, h, w]`` (segmentation), containing
            zeroes and ones.

        Returns
        -------
            The result of Equation (2) from :cite:p:`guler_refining_2024`.

        Raises
        ------
        AssertionError
            In case the weights have not be initialized by calling
            :py:meth:`get_arguments_from_datamodule`.
        """

        assert self.weights is not None, (
            f"Weights are not initialized. Call "
            f"{self.__class__.__name__}.get_arguments_from_datamodule() to sort this."
        )

        if len(input_.shape) > 2:  # segmentation
            input_ = input_.transpose(0, 2).transpose(1, 3).reshape(-1, input_.shape[1])
            target = target.transpose(0, 2).transpose(1, 3).reshape(-1, target.shape[1])

        weights = ((1.0 - target) * self.weights[0]) + (target * self.weights[1])

        individual_losses = torch.nn.functional.binary_cross_entropy_with_logits(
            input_, target, reduction="none"
        )

        return (individual_losses * weights).mean()

    def to(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        """Move loss parameters to specified device.

        Refer to the method :py:meth:`torch.nn.Module.to` for details.

        Parameters
        ----------
        *args
            Parameter forwarded to the underlying implementations.
        **kwargs
            Parameter forwarded to the underlying implementations.

        Returns
        -------
            Self.
        """

        if self.weights is None:
            logger.warning(
                f"Weights are not initialized. Call {self.__class__.__name__}."
                f"get_arguments_from_datamodule() to sort this."
            )

            return self

        self.weights = self.weights.to(*args, **kwargs)

        return self
