# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import pathlib
import typing

import h5py
import lightning.pytorch
import lightning.pytorch.callbacks
import torch.utils.data
import tqdm

from ...engine.device import DeviceManager
from ...utils.string import rewrap

logger = logging.getLogger(__name__)


class _HDF5Writer(lightning.pytorch.callbacks.BasePredictionWriter):
    """Write HDF5 files for each sample processed by our model.

    Objects of this class can also keep track of samples written to disk and
    return a summary list.

    Parameters
    ----------
    output_folder
        Base directory where to write predictions to.

    write_interval
        When will this callback be active.
    """

    def __init__(
        self,
        output_folder: pathlib.Path,
        write_interval: typing.Literal["batch", "epoch", "batch_and_epoch"] = "batch",
    ):
        super().__init__(write_interval=write_interval)
        self.output_folder = output_folder
        self._data: list[tuple[str, str]] = []

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

        for k, sample_pred in enumerate(prediction):
            sample_name: str = batch["name"][k]
            stem = pathlib.Path(sample_name).with_suffix(".hdf5")
            output_path = self.output_folder / stem
            tqdm.tqdm.write(f"`{sample_name}` -> `{str(output_path)}`")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with h5py.File(output_path, "w") as f:
                f.create_dataset(
                    "image",
                    data=batch["image"][k].cpu().numpy(),
                    compression="gzip",
                    compression_opts=9,
                )
                f.create_dataset(
                    "prediction",
                    data=sample_pred.cpu().numpy().squeeze(0),
                    compression="gzip",
                    compression_opts=9,
                )
                f.create_dataset(
                    "target",
                    data=(batch["target"][k].squeeze(0).cpu().numpy() > 0.5),
                    compression="gzip",
                    compression_opts=9,
                )
                f.create_dataset(
                    "mask",
                    data=(batch["mask"][k].squeeze(0).cpu().numpy() > 0.5),
                    compression="gzip",
                    compression_opts=9,
                )
            self._data.append((sample_name, str(stem)))

    def reset(self) -> list[tuple[str, str]]:
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
    output_folder: pathlib.Path,
) -> (
    dict[str, list[tuple[str, str]]]
    | list[list[tuple[str, str]]]
    | list[tuple[str, str]]
    | None
):
    """Run inference on input data, output predictions.

    Parameters
    ----------
    model
        Neural network model (e.g. lwnet).
    datamodule
        The lightning DataModule to run predictions on.
    device_manager
        An internal device representation, to be used for prediction. This
        representation can be converted into a pytorch device or a lightning
        accelerator setup.
    output_folder
        Folder where to store HDF5 representations of probability maps.

    Returns
    -------
        A JSON-able representation of sample data stored at ``output_folder``.
        For every split (dataloader), a list of samples in the form
        ``[sample-name, hdf5-path]`` is returned.  In the cases where the
        ``predict_dataloader()`` returns a single loader, we then return a
        list.  A dictionary is returned in case ``predict_dataloader()`` also
        returns a dictionary.

    Raises
    ------
    TypeError
        If the DataModule's ``predict_dataloader()`` method does not return any
        of the types described above.
    """

    from lightning.pytorch.loggers.logger import DummyLogger

    collector = _HDF5Writer(output_folder)

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
        return retval_list

    if isinstance(dataloaders, dict):
        retval_dict = {}
        for name, dataloader in dataloaders.items():
            logger.info(f"Running prediction on `{name}` split...")
            trainer.predict(model, dataloader, return_predictions=False)
            retval_dict[name] = collector.reset()
        return retval_dict

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
