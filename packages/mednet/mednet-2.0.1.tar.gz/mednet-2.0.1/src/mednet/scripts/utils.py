# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Utilities for command-line scripts."""

import json
import logging
import pathlib
import re
import shutil
import typing

import compact_json
import lightning.pytorch
import lightning.pytorch.callbacks
import numpy
import torch.nn
from click import BadParameter
from pydantic import TypeAdapter
from pydantic.types import StringConstraints

from ..engine.device import SupportedPytorchDevice

logger = logging.getLogger(__name__)

JSONable: typing.TypeAlias = (
    typing.Mapping[str, "JSONable"]
    | typing.Sequence["JSONable"]
    | str
    | int
    | float
    | bool
    | None
)
"""Defines types that can be encoded in a JSON string."""

CheckpointMetricType: typing.TypeAlias = typing.Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^(min|max)/.+$",
    ),
]
"""
Defines a type for the metric used to track and save the best
checkpoint of a model. This type represents a constrained string
in the format 'mode/metric', where:
- 'mode' is either 'min' or 'max', indicating the optimization direction;
- 'metric' is a non-empty string specifying the name of the evaluation
metric (e.g., 'loss', 'auc').
"""


def parse_checkpoint_metric(value: str) -> tuple[str, typing.Literal["min", "max"]]:
    """Validate and then parse the string as a 'CheckpointMetricType'.

    Parameters
    ----------
    value
        The string to be validated and then parsed.

    Returns
    -------
    The name of the metric used for saving the best checkpoint and the modality
    {'min', 'max'} in this exact order.
    """
    adapter = TypeAdapter(CheckpointMetricType)
    try:
        validated = adapter.validate_python(value)
    except Exception as e:
        raise BadParameter(
            f"Invalid format: '{value.strip()}'. Must match 'min/<metric>' or 'max/<metric>'."
        ) from e

    mode, metric = validated.split("/", 1)
    return metric, mode


def model_summary(
    model: torch.nn.Module,
) -> dict[str, int | list[tuple[str, str, int]]]:
    """Save a little summary of the model in a txt file.

    Parameters
    ----------
    model
        Instance of the model for which to save the summary.

    Returns
    -------
    tuple[lightning.pytorch.callbacks.ModelSummary, int]
        A tuple with the model summary in a text format and number of parameters of the model.
    """

    s = lightning.pytorch.utilities.model_summary.ModelSummary(  # type: ignore
        model,
    )

    return dict(
        model_summary=list(zip(s.layer_names, s.layer_types, s.param_nums)),
        model_size=s.total_parameters,
    )


def device_properties(
    device_type: SupportedPytorchDevice,
) -> dict[str, int | float | str]:
    """Generate information concerning hardware properties.

    Parameters
    ----------
    device_type
        The type of compute device we are using.

    Returns
    -------
        Static properties of the current machine.
    """

    from ..utils.resources import cpu_constants, cuda_constants, mps_constants

    retval: dict[str, int | float | str] = {}
    retval.update(cpu_constants())

    match device_type:
        case "cpu":
            pass
        case "cuda":
            results = cuda_constants()
            if results is not None:
                retval.update(results)
        case "mps":
            results = mps_constants()
            if results is not None:
                retval.update(results)
        case _:
            pass

    return retval


def execution_metadata() -> dict[str, int | float | str | dict[str, str] | list[str]]:
    """Produce metadata concerning the running script, in the form of a
    dictionary.

    This function returns potentially useful metadata concerning program
    execution.  It contains a certain number of preset variables.

    Returns
    -------
        A dictionary that contains the following fields:

        * ``package-name``: current package name (e.g. ``mednet``)
        * ``package-version``: current package version (e.g. ``1.0.0b0``)
        * ``datetime``: date and time in ISO8601 format (e.g. ``2024-02-23T18:38:09+01:00``)
        * ``user``: username (e.g. ``johndoe``)
        * ``conda-env``: if set, the name of the current conda environment
        * ``path``: current path when executing the command
        * ``command-line``: the command-line that is being run
        * ``hostname``: machine hostname (e.g. ``localhost``)
        * ``platform``: machine platform (e.g. ``darwin``)
        * ``accelerator``: acceleration devices available (e.g. ``cuda``)
    """

    import datetime
    import importlib.metadata
    import importlib.util
    import os
    import sys

    args: list[str] = []
    for k in sys.argv:
        if " " in k:
            args.append(f"'{k}'")
        else:
            args.append(k)

    # current date time, in ISO8610 format
    current_datetime = datetime.datetime.now().astimezone().isoformat()

    # collects dependency information
    package_name = __package__.split(".")[0] if __package__ is not None else "unknown"
    requires = importlib.metadata.requires(package_name) or []
    dependence_names = [re.split(r"(\=|~|!|>|<|;|\s)+", k)[0] for k in requires]
    installed = {
        v[0]: k for k, v in importlib.metadata.packages_distributions().items()
    }
    dependencies = {
        k: importlib.metadata.version(k)  # version number as str
        for k in sorted(dependence_names)
        if importlib.util.find_spec(k if k not in installed else installed[k])
        is not None  # if is installed
    }

    # checks if the current version corresponds to a dirty (uncommitted) change
    # set, issues a warning to the user
    current_version = importlib.metadata.version(package_name)
    try:
        import versioningit

        actual_version = versioningit.get_version(".")
        if current_version != actual_version:
            logger.warning(
                f"Version mismatch between current version set "
                f"({current_version}) and actual version returned by "
                f"versioningit ({actual_version}).  This typically happens "
                f"when you commit changes locally and do not re-install the "
                f"package. Run `pixi update {package_name}`, `pip install -e .` "
                f"or equivalent to fix this.",
            )
    except Exception as e:
        # not in a git repo?
        logger.debug(f"Error {e}")
        pass

    # checks if any acceleration device is present in the current platform
    accelerators = [f"cpu ({torch.backends.cpu.get_cpu_capability()})"]

    if torch.cuda.is_available() and torch.backends.cuda.is_built():
        accelerators.append("cuda")

    if torch.backends.cudnn.is_available():
        accelerators.append("cudnn")

    if torch.backends.mps.is_available():
        accelerators.append("mps")

    if torch.backends.mkl.is_available():
        accelerators.append("mkl")

    if torch.backends.mkldnn.is_available():
        accelerators.append("mkldnn")

    if torch.backends.openmp.is_available():
        accelerators.append("openmp")

    python = {
        "version": ".".join([str(k) for k in sys.version_info[:3]]),
        "path": sys.executable,
    }

    return {
        "datetime": current_datetime,
        "package-name": package_name,
        "package-version": current_version,
        "python": python,
        "dependencies": dependencies,
        "user": __import__("getpass").getuser(),
        "conda-env": os.environ.get("CONDA_DEFAULT_ENV", ""),
        "path": os.path.realpath(os.curdir),
        "command-line": " ".join(args),
        "hostname": __import__("platform").node(),
        "platform": sys.platform,
        "accelerators": accelerators,
    }


class NumpyJSONEncoder(json.JSONEncoder):
    """Extends the standard JSON encoder to support Numpy arrays."""

    def default(self, o: typing.Any) -> typing.Any:
        """If input object is a ndarray it will be converted into a list.

        Parameters
        ----------
        o
            Input object to be JSON serialized.

        Returns
        -------
            A serializable representation of object ``o``.
        """

        if isinstance(o, numpy.ndarray):
            try:
                retval = o.tolist()
            except TypeError:
                pass
            else:
                return retval
        elif isinstance(o, numpy.generic):
            try:
                retval = o.item()
            except TypeError:
                pass
            else:
                return retval

        # Let the base class default method raise the TypeError
        return super().default(o)


def save_json_with_backup(path: pathlib.Path, data: JSONable) -> None:
    """Save a dictionary into a JSON file with path checking and backup.

    This function will save a dictionary into a JSON file.  It will check to
    the existence of the directory leading to the file and create it if
    necessary.  If the file already exists on the destination folder, it is
    backed-up before a new file is created with the new contents.

    Parameters
    ----------
    path
        The full path where to save the JSON data.
    data
        The data to save on the JSON file.
    """

    formatter = compact_json.Formatter()
    # only only 2 indent spaces for further levels
    formatter.indent_spaces = 2
    # controls how much nesting can happen
    formatter.max_inline_complexity = 2
    # controls the maximum line width (has priority over nesting)
    formatter.max_inline_length = 88
    # remove any trailing whitespaces
    formatter.omit_trailing_whitespace = True

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.parent / (path.name + "~")
        shutil.copy(path, backup)

    data = json.loads(json.dumps(data, indent=2, cls=NumpyJSONEncoder))
    formatter.dump(data, str(path))


def save_json_metadata(
    output_file: pathlib.Path,
    **kwargs: typing.Any,
) -> None:  # numpydoc ignore=PR01
    """Save prediction hyperparameters into a .json file."""

    from ..data.datamodule import ConcatDataModule
    from ..engine.device import DeviceManager
    from ..models.model import Model
    from .utils import (
        device_properties,
        execution_metadata,
        model_summary,
        save_json_with_backup,
    )

    json_data: dict[str, typing.Any] = execution_metadata()

    for key, value in kwargs.items():
        match value:
            case ConcatDataModule():
                json_data["database_name"] = value.database_name
                json_data["database_split"] = value.split_name
            case Model():
                json_data["model"] = f"{type(value).__module__}.{type(value).__name__}"
                json_data.update(model_summary(value))
            case pathlib.Path():
                json_data[key] = str(value)
            case DeviceManager():
                json_data.update(device_properties(value.device_type))
            case list() if key == "augmentations":
                if len(value) != 0:
                    json_data[key] = [f"{type(k).__module__}.{str(k)}" for k in value]
                else:
                    json_data[key] = []
            case _:
                json_data[key] = value

    json_data = {k.replace("_", "-"): v for k, v in json_data.items()}
    logger.info(f"Writing run metadata at `{output_file}`...")
    save_json_with_backup(output_file, json_data)


def get_ckpt_metric_mode(
    train_metadata_file: pathlib.Path,
    default_metric: str = "loss",
    default_mode: typing.Literal["min", "max"] = "min",
) -> tuple[str, typing.Literal["min", "max"]]:
    """Retrieve information regarding the metric and modality used to save the best
    checkpoint of the model by looking at the train metadata in the json file.

    Parameters
    ----------
    train_metadata_file
        Path of the train.meta.json file.
    default_metric
        The metric name to return when no metric information is found in train.meta
        JSON file. The default value is set to "loss".
    default_mode
        The modality of evaluation to return when no mode information is found in
        train.meta JSON file. The default value is set to "min".

    Returns
    -------
        The name of the metric used for saving the best checkpoint and the modality
        {'min', 'max'} in this exact order.
    """

    with train_metadata_file.open("r") as f:
        train_metadata = json.load(f)

    metric = (
        train_metadata["checkpoint-metric"]
        if "checkpoint-metric" in train_metadata
        else default_metric
    )
    mode = (
        train_metadata["checkpoint-mode"]
        if "checkpoint-mode" in train_metadata
        else default_mode
    )
    return metric, mode
