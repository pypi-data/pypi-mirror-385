# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Support for switching execution devices (GPU vs CPU)."""

import logging
import os
import typing

import torch
import torch.backends

logger = logging.getLogger(__name__)


SupportedPytorchDevice: typing.TypeAlias = typing.Literal[
    "cpu",
    "cuda",
    "mps",
]
"""List of supported pytorch devices by this library."""


def _split_int_list(s: str) -> list[int]:
    """Split a list of integers encoded in a string (e.g. "1,2,3") into a
    Python list of integers (e.g. ``[1, 2, 3]``).

    Parameters
    ----------
    s
        A list of integers encoded in a string.

    Returns
    -------
    list[int]
        A Python list of integers.
    """

    return [int(k.strip()) for k in s.split(",")]


class DeviceManager:
    r"""Manage Lightning Accelerator and Pytorch Devices.

    It takes the user input, in the form of a string defined by
    ``[\S+][:\d[,\d]?]?`` (e.g.: ``cpu``, ``mps``, or ``cuda:3``), and can
    translate to the right incarnation of Pytorch devices or Lightning
    Accelerators to interface with the various frameworks.

    Instances of this class also manage the environment variable
    ``$CUDA_VISIBLE_DEVICES`` if necessary.

    Parameters
    ----------
    name
        The name of the device to use, in the form of a string defined by
        ``[\S+][:\d[,\d]?]?`` (e.g.: ``cpu``, ``mps``, or ``cuda:3``).  In
        the specific case of ``cuda``, one can also specify a device to use
        either by adding ``:N``, where N is the zero-indexed board number on
        the computer, or by setting the environment variable
        ``$CUDA_VISIBLE_DEVICES`` with the devices that are usable by the
        current process.
    """

    def __init__(self, name: SupportedPytorchDevice):
        parts = name.split(":", 1)

        # make device type of the right Python type
        if parts[0] not in typing.get_args(SupportedPytorchDevice):
            raise ValueError(f"Unsupported device-type `{parts[0]}`")
        self.device_type: SupportedPytorchDevice = typing.cast(
            SupportedPytorchDevice,
            parts[0],
        )

        self.device_ids: list[int] = []
        if len(parts) > 1:
            self.device_ids = _split_int_list(parts[1])

        if self.device_type == "cuda":
            visible_env = os.environ.get("CUDA_VISIBLE_DEVICES")
            if visible_env:
                visible = _split_int_list(visible_env)
                if self.device_ids and visible != self.device_ids:
                    logger.warning(
                        f"${{CUDA_VISIBLE_DEVICES}}={visible} and name={name} "
                        f"- overriding environment with value set on `name`",
                    )
                else:
                    self.device_ids = visible

            # make sure that it is consistent with the environment
            if self.device_ids:
                os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(
                    [str(k) for k in self.device_ids],
                )

        if self.device_type not in typing.get_args(SupportedPytorchDevice):
            raise RuntimeError(
                f"Unsupported device type `{self.device_type}`. "
                f"Supported devices types are "
                f"`{', '.join(typing.get_args(SupportedPytorchDevice))}`",
            )

        if self.device_ids and self.device_type in ("cpu", "mps"):
            logger.warning(
                f"Cannot pin device ids if using cpu or mps backend. "
                f"Setting `name` to {name} is non-sensical.  Ignoring...",
            )

        # check if the device_type that was set has support compiled in
        if self.device_type == "cuda":
            assert hasattr(torch, "cuda") and torch.cuda.is_available(), (
                f"User asked for device = `{name}`, but CUDA support is "
                f"not compiled into pytorch!"
            )

        if self.device_type == "mps":
            assert (
                hasattr(torch.backends, "mps") and torch.backends.mps.is_available()  # type:ignore
            ), (
                f"User asked for device = `{name}`, but MPS support is "
                f"not compiled into pytorch!"
            )

    def torch_device(self) -> torch.device:
        """Return a representation of the torch device to use by default.

        .. warning::

           If a list of devices is set, then this method only returns the first
           device.  This may impact Nvidia GPU logging in the case multiple
           GPU cards are used.

        Returns
        -------
        torch.device
            The **first** torch device (if a list of ids is set).
        """

        if self.device_type in ("cpu", "mps"):
            return torch.device(self.device_type)

        if self.device_type == "cuda":
            if not self.device_ids:
                return torch.device(self.device_type)

            return torch.device(self.device_type, self.device_ids[0])

        # if you get to this point, this is an unexpected RuntimeError
        raise RuntimeError(
            f"Unexpected device type {self.device_type} lacks support",
        )

    def lightning_accelerator(self) -> tuple[str, int | list[int] | str]:
        """Return the lightning accelerator setup.

        Returns
        -------
        accelerator
            The lightning accelerator to use.
        devices
            The lightning devices to use.
        """

        devices: int | list[int] | str = self.device_ids
        if not devices:
            devices = "auto"
        elif self.device_type == "mps":
            devices = 1

        return self.device_type, devices
