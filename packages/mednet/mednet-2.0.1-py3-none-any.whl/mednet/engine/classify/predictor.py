# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prediction engine for classification tasks."""

import logging
import typing

import lightning.pytorch.callbacks
import torch.utils.data

from ...engine.device import DeviceManager
from ...models.classify.typing import Prediction, PredictionSplit
from ...utils.string import rewrap

logger = logging.getLogger(__name__)


class _JSONMetadataCollector(lightning.pytorch.callbacks.BasePredictionWriter):
    """Collects further sample metadata to store with predictions.

    This object collects further sample metadata we typically keep with
    predictions.

    Parameters
    ----------
    write_interval
        When will this callback be active.
    """

    def __init__(
        self,
        write_interval: typing.Literal["batch", "epoch", "batch_and_epoch"] = "batch",
    ):
        super().__init__(write_interval=write_interval)
        self._data: list[Prediction] = []

    def write_on_batch_end(
        self,
        trainer: lightning.pytorch.Trainer,
        pl_module: lightning.pytorch.LightningModule,
        prediction: typing.Any,
        batch_indices: typing.Sequence[int] | None,
        batch: typing.Any,
        batch_idx: int,
        dataloader_idx: int,
    ) -> None:
        """Write batch predictions to disk.

        Parameters
        ----------
        trainer
            The trainer being used.
        pl_module
            The pytorch module.
        prediction
            The actual predictions to record.
        batch_indices
            The relative position of samples on the epoch.
        batch
            The current batch.
        batch_idx
            Index of the batch overall.
        dataloader_idx
            Index of the dataloader overall.
        """
        del trainer, pl_module, batch_indices, batch_idx, dataloader_idx

        target_shape = batch["target"][0].shape
        prediction_shape = prediction[0].shape

        if prediction_shape != target_shape:
            # Multiclass problems
            # NOTE: mednet datamodules which implement multiclass problems should return target with shape torch.size([]) otherwise
            # this code will not work properly. The decision comes from the fact that CrossEntropyLoss expects target with shape torch.size([])
            batch["target"] = batch["target"].unsqueeze(
                1
            )  # The expected target sample is a 1D tensor.

        for k, sample_pred in enumerate(prediction):
            sample_name: str = batch["name"][k]
            if prediction_shape == target_shape:
                # Binary and Multilabel problems have same target and prediction shape: (1,) for binary and (C,) for multilabel
                sample_pred_to_store = (
                    sample_pred.cpu().numpy().reshape(target_shape).tolist()
                )
            else:
                # For Multiclass scenario the prediction shape is (C,) but the target is (1,) since it is a single value between [0, C-1]
                sample_pred_to_store = sample_pred.cpu().numpy().tolist()

            self._data.append(
                (
                    sample_name,
                    batch["target"][k].cpu().int().numpy().tolist(),
                    sample_pred_to_store,
                )
            )

    def reset(self) -> list[Prediction]:
        """Summary of written objects.

        Also resets the internal state.

        Returns
        -------
            A list containing a summary of all samples written.
        """
        retval = self._data
        self._data = []
        return retval


def run(
    model: lightning.pytorch.LightningModule,
    datamodule: lightning.pytorch.LightningDataModule,
    device_manager: DeviceManager,
) -> list[Prediction] | list[list[Prediction]] | PredictionSplit | None:
    """Run inference on input data, output predictions.

    Parameters
    ----------
    model
        Neural network model (e.g. pasa).
    datamodule
        The lightning DataModule to run predictions on.
    device_manager
        An internal device representation, to be used for training and
        validation.  This representation can be converted into a pytorch device
        or a lightning accelerator setup.

    Returns
    -------
        Depending on the return type of the DataModule's
        ``predict_dataloader()`` method:

            * if :py:class:`torch.utils.data.DataLoader`, then returns a
              :py:class:`list` of predictions.
            * if :py:class:`list` of :py:class:`torch.utils.data.DataLoader`, then
              returns a list of lists of predictions, each list corresponding to
              the iteration over one of the dataloaders.
            * if :py:class:`dict` of :py:class:`str` to
              :py:class:`torch.utils.data.DataLoader`, then returns a dictionary
              mapping names to lists of predictions.
            * if ``None``, then returns ``None``.

    Raises
    ------
    TypeError
        If the DataModule's ``predict_dataloader()`` method does not return any
        of the types described above.
    """

    from lightning.pytorch.loggers.logger import DummyLogger

    collector = _JSONMetadataCollector()

    accelerator, devices = device_manager.lightning_accelerator()
    trainer = lightning.pytorch.Trainer(
        accelerator=accelerator,
        devices=devices,
        logger=DummyLogger(),
        callbacks=[collector],
    )

    dataloaders = datamodule.predict_dataloader()

    if isinstance(dataloaders, torch.utils.data.DataLoader):
        logger.info("Running prediction on a single dataloader...")
        trainer.predict(model, dataloaders, return_predictions=False)
        return collector.reset()

    if isinstance(dataloaders, list):
        retval_list = []
        for k, dataloader in enumerate(dataloaders):
            logger.info(f"Running prediction on split `{k}`...")
            trainer.predict(model, dataloader, return_predictions=False)
            retval_list.append(collector.reset())
        return retval_list  # type: ignore

    if isinstance(dataloaders, dict):
        retval_dict = {}
        for name, dataloader in dataloaders.items():
            logger.info(f"Running prediction on `{name}` split...")
            trainer.predict(model, dataloader, return_predictions=False)
            retval_dict[name] = collector.reset()
        return retval_dict  # type: ignore

    if dataloaders is None:
        logger.warning("Datamodule did not return any prediction dataloaders!")
        return None

    # if you get to this point, then the user is returning something that is
    # not supported - complain!
    raise TypeError(
        rewrap(
            f"""Datamodule returned strangely typed prediction dataloaders:
            `{type(dataloaders)}` - if this is not an error, write code to support this
            use-case."""
        )
    )
