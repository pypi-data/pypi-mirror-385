# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import pathlib
import typing

import h5py
import lightning.pytorch
import torch.utils.data
import tqdm

logger = logging.getLogger(__name__)


def run(
    datamodule: lightning.pytorch.LightningDataModule,
    output_folder: pathlib.Path,
) -> (
    dict[str, list[tuple[str, str]]]
    | list[list[tuple[str, str]]]
    | list[tuple[str, str]]
    | None
):
    """Dump annotations from input datamodule.

    Parameters
    ----------
    datamodule
        The lightning DataModule to extract annotations from.
    output_folder
        Folder where to store HDF5 representations of annotations.

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

    def _write_sample(
        sample: typing.Any, output_folder: pathlib.Path
    ) -> tuple[str, str]:
        """Write a single sample target to an HDF5 file.

        Parameters
        ----------
        sample
            A segmentation sample as output by a dataloader.
        output_folder
            Path leading to a folder where to store dumped annotations.

        Returns
        -------
            A tuple which contains the sample path and the destination
            directory where the HDF5 file was saved.
        """
        name = sample["name"][0]
        stem = pathlib.Path(name).with_suffix(".hdf5")
        dest = output_folder / stem
        tqdm.tqdm.write(f"`{name}` -> `{str(dest)}`")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with h5py.File(dest, "w") as f:
            f.create_dataset(
                "image",
                data=sample["image"][0].cpu().numpy(),
                compression="gzip",
                compression_opts=9,
            )
            f.create_dataset(
                "target",
                data=(sample["target"][0].squeeze(0).cpu().numpy() > 0.5),
                compression="gzip",
                compression_opts=9,
            )
            f.create_dataset(
                "mask",
                data=(sample["mask"][0].squeeze(0).cpu().numpy() > 0.5),
                compression="gzip",
                compression_opts=9,
            )
        return (name, str(stem))

    dataloaders = datamodule.predict_dataloader()

    if isinstance(dataloaders, torch.utils.data.DataLoader):
        logger.info("Dump annotations from a single dataloader...")
        return [_write_sample(k, output_folder) for k in tqdm.tqdm(dataloaders)]

    if isinstance(dataloaders, list):
        retval_list = []
        for k, dataloader in enumerate(dataloaders):
            logger.info(f"Dumping annotations from split `{k}`...")
            retval_list.append(
                [_write_sample(k, output_folder) for k in tqdm.tqdm(dataloader)]
            )
        return retval_list

    if isinstance(dataloaders, dict):
        retval_dict = {}
        for name, dataloader in dataloaders.items():
            logger.info(f"Dumping annotations from split `{name}`...")
            retval_dict[name] = [
                _write_sample(k, output_folder) for k in tqdm.tqdm(dataloader)
            ]
        return retval_dict

    if dataloaders is None:
        logger.warning("Datamodule did not return any prediction dataloaders!")
        return None

    # if you get to this point, then the user is returning something that is
    # not supported - complain!
    raise TypeError(
        f"Datamodule returned strangely typed prediction "
        f"dataloaders: `{type(dataloaders)}` - Please write code "
        f"to support this use-case.",
    )
