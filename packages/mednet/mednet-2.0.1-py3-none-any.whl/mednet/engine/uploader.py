# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Functions to upload models and measures to GitLab's experiment registry."""

import configparser
import json
import logging
import os
import pathlib
import re
import shutil
import tempfile
import typing

import gitlab
import mlflow

from ..scripts.utils import get_ckpt_metric_mode
from ..utils.checkpointer import get_checkpoint_to_run_inference

logger = logging.getLogger(__name__)


def _gitlab_instance_and_token() -> tuple[gitlab.Gitlab, str]:
    """Return an instance of the Gitlab object for remote operations, and the
    user token.

    Returns
    -------
        Gitlab main object and user token
    """

    cfg = pathlib.Path("~/.python-gitlab.cfg").expanduser()
    if cfg.exists():
        gl = gitlab.Gitlab.from_config("idiap", [str(cfg)])
        config = configparser.ConfigParser()
        config.read(cfg)
        token = config["idiap"]["private_token"]

    else:  # ask the user for a token or use one from the current runner
        server = "https://gitlab.idiap.ch"
        token = input(f"{server} (user or project) token: ")
        gl = gitlab.Gitlab(server, private_token=token, api_version="4")

    # tests authentication with given credential.
    gl.auth()

    return gl, token


def _size_in_mb(path: pathlib.Path) -> float:
    """Return the size in megabytes of a file.

    Parameters
    ----------
    path
        Input path to calculate file size from.

    Returns
    -------
        A floating point number for the size of the object in MB.
    """
    return path.stat().st_size / (1024**2)


def _assemble_artifacts(
    experiment_folder: pathlib.Path, upload_limit_mb: int
) -> tempfile.TemporaryDirectory:
    """Assemble artifacts (files) to upload, sanitize filenames and check overall upload
    size.

    The files that are uploaded are the following:

    * train.meta.json: meta information during training
    * trainlog.pdf: evolution of tracked training variables
    * evaluation.json: evaluation results
    * evaluation.meta.json: meta information during evaluation
    * evaluation.rst: evaluation results in table format
    * evaluation.pdf: evaluation plots
    * model checkpoint (variable name)

    Parameters
    ----------
    experiment_folder
        Directory in which to upload results from.
    upload_limit_mb
        Maximim upload size in MB (set to 0 for no limit).

    Returns
    -------
        Temporary directory where the important files from the experiment
        folder have been assembled and names sanitized.

    Raises
    ------
    AssertionError
        In case one of the necessary files that are typically uploaded is
        missing.
    RuntimeError
        In case the total size of the temporary directory contents is larger,
        in MB, than the ``upload_limit_mb``.
    """

    logger.info(f"Assembling files from {experiment_folder}...")

    # get train files
    train_folder = experiment_folder
    train_log_file = train_folder / "trainlog.pdf"
    train_meta_file = train_folder / "train.meta.json"
    metric, mode = get_ckpt_metric_mode(train_meta_file)
    train_model_file = get_checkpoint_to_run_inference(train_folder, metric, mode)
    train_files = [train_meta_file, train_model_file, train_log_file]

    # get evaluation files
    evaluation_file = experiment_folder / "evaluation.json"
    evaluation_meta_file = experiment_folder / "evaluation.meta.json"
    evaluation_meta_file = experiment_folder / "evaluation.rst"
    evaluation_log_file = experiment_folder / "evaluation.pdf"
    evaluation_files = [
        evaluation_file,
        evaluation_meta_file,
        evaluation_log_file,
    ]

    # checks all files exist
    for f in train_files + evaluation_files:
        assert f.exists(), f"Missing file `{f}` - cannot upload artifact"

    # checks for maximum upload limit
    total_size_mb = sum([_size_in_mb(f) for f in train_files + evaluation_files])
    if upload_limit_mb != 0 and total_size_mb > upload_limit_mb:
        raise RuntimeError(
            f"Total size of upload ({total_size_mb:.2f} MB) exceeds "
            f"permitted maximum ({upload_limit_mb:.2f} MB)."
        )

    retval = tempfile.TemporaryDirectory()
    tmpdir_path = pathlib.Path(retval.name)
    for f in train_files + evaluation_files:
        clean = tmpdir_path / f.parts[-1].replace("=", "-")
        shutil.copy2(f, clean)
        logger.debug(f"`{str(f)}` -> `{str(clean)}` ({_size_in_mb(f):.2f} MB)")

    logger.info(f"Total size of files at {retval.name} = {total_size_mb:.2f} MB")
    return retval


def _check_version(version: str) -> None:
    """Check if a provided version number is not dirty compatible.

    Checks if the version of the model to be uploaded is not dirty (i.e. ends
    with something like ``.d20240807``).

    Parameters
    ----------
    version
        A string indicating the model version (e.g. "1.0.0").
    """

    assert not re.search(r"\.d[0-9]*$", version), (
        f"Incompatible model version ({version}) - you should NOT "
        f"upload models from `dirty` repositories"
    )


def _assemble_parameters(basedir: pathlib.Path) -> dict[str, typing.Any]:
    """Assemble parameters to log to experiment.

    Parameters are forcebly converted to string representations via the MLflow
    interface.

    Parameters
    ----------
    basedir
        Base directory where to find the file ``train.meta.json``.  Typically,
        this is the experiment folder.

    Returns
    -------
        A dictionary that maps strings to any value that, itself, can be
        converted to a string.  The MLflow interface will take care of this.
    """

    train_meta_file = basedir / "train.meta.json"
    with train_meta_file.open("r") as meta_file:
        train_data = json.load(meta_file)

    _check_version(train_data["package-version"])

    # get lowest validation epoch
    train_model_file = get_checkpoint_to_run_inference(
        basedir, train_data["checkpoint-metric"], train_data["checkpoint-mode"]
    )
    best_epoch = int(str(train_model_file).split(".")[0].rsplit("=", 1)[1])

    return {
        "package version": train_data["package-version"],
        "batch size": train_data["batch-size"],
        "batch accumulations": train_data["accumulate-grad-batches"],
        "epochs": train_data["epochs"],
        "model epoch": best_epoch,
    }


def _assemble_metrics(basedir: pathlib.Path, names: list[str]) -> dict[str, float]:
    """Assemble metrics to log to experiment.

    Metrics are float values that can use to measure the performance of a
    model.

    Parameters
    ----------
    basedir
        Base directory where to find the file ``evaluation.json``.  Typically,
        this is the experiment folder.
    names
        A list of metrics we are interested in fetching from the evaluation
        file, and export to GitLab.

    Returns
    -------
        A dictionary that maps strings to floating point values.
    """

    evaluation_file = basedir / "evaluation.json"
    with evaluation_file.open("r") as f:
        evaluation_data = json.load(f)

    return {k: v for k, v in evaluation_data["test"].items() if k in names}


def _user_or_default_names(
    basedir: pathlib.Path, experiment_name: str, run_name: str
) -> tuple[str, str]:
    """Assert user-provided experiment and run names or defaults.

    Parameters
    ----------
    basedir
        Base directory where to find the file ``train.meta.json``.  Typically,
        this is the experiment folder.
    experiment_name
        User provided experiment name.  If empty, then a default experiment
        name will be proposed.
    run_name
        User provided run name.  If empty, then a default run name using the
        experiment date will be proposed.

    Returns
    -------
        A tuple containing the experiment and run name to be used.
    """

    train_meta_file = basedir / "train.meta.json"
    with train_meta_file.open("r") as meta_file:
        train_data = json.load(meta_file)

    return (
        experiment_name or f"{train_data['model-name']}-{train_data['database-name']}",
        run_name or train_data["datetime"],
    )


def _upload_ml_experiment(
    project_path: str,
    experiment_name: str,
    run_name: str,
    artifact_path: pathlib.Path,
    parameters: dict[str, typing.Any],
    metrics: dict[str, float],
) -> None:
    """Upload to GitLab using the Machine Learning Experiment Tracking
    interface.

    Information about the ML Experiment Tracking interface can be found at
    https://docs.gitlab.com/ee/user/project/ml/experiment_tracking/

    Parameters
    ----------
    project_path
        Path to the project where to upload model entries.
    experiment_name
        A string indicating the experiment name (e.g. "exp-pasa-mc" or "exp-densenet-mc-ch").
    run_name
        A string indicating the run name (e.g. "run-1").
    artifact_path
        A base directory in which all contained files will be uploaded as
        artifacts to the experiment entry.
    parameters
        All experiment parameters (``str`` -> ``str``) to log to the
        experiment table.
    metrics
        All experiment metrics (``str`` -> ``float``) to log to the experiment
        table.
    """

    logger.info("Retrieving GitLab credentials for access to hosted MLFlow server...")
    gitlab, token = _gitlab_instance_and_token()
    project = gitlab.projects.get(project_path)
    os.environ["MLFLOW_TRACKING_TOKEN"] = token
    os.environ["MLFLOW_TRACKING_URI"] = (
        gitlab.api_url + f"/projects/{project.id}/ml/mlflow"
    )

    logger.info(
        f"Uploading entry `{run_name}` to experiment `{experiment_name}` "
        f"on GitLab project `{project.name_with_namespace}` (id: {project.id})..."
    )
    exp_meta = mlflow.set_experiment(experiment_name=experiment_name)

    with mlflow.start_run(run_name=run_name):
        logger.info("Uploading parameters...")
        for key, value in parameters.items():
            logger.info(f'[parameter] "{key}" = "{str(value)}"')
            mlflow.log_param(key, value, synchronous=True)

        logger.info("Uploading metrics...")
        for key, value in metrics.items():
            logger.info(f'[metric] "{key}" = {value:.3g}')
            mlflow.log_metric(key, value, synchronous=True)

        logger.info("Uploading artifacts (files)...")
        for f in artifact_path.glob("*.*"):
            logger.info(f'[artifact] "{str(f)}" ({_size_in_mb(f):.2f} MB)')
            mlflow.log_artifact(str(f))

    logger.info(
        f"Visit {gitlab.url}/{project.path_with_namespace}/-/ml/experiments/{exp_meta.experiment_id}"
    )


def run(
    project_path: str,
    experiment_folder: pathlib.Path,
    experiment_name: str,
    run_name: str,
    metrics: list[str],
    upload_limit_mb: int,
) -> None:
    """Upload results from an experiment folder to GitLab's MLFlow server.

    Parameters
    ----------
    project_path
        Path to the project where to upload model entries.
    experiment_folder
        Directory in which to upload results from.
    experiment_name
        A string indicating the experiment name (e.g. "exp-pasa-mc" or "exp-densenet-mc-ch").
    run_name
        A string indicating the run name (e.g. "run-1").
    metrics
        List of metrics to upload.
    upload_limit_mb
        Maximim upload size in MB (set to 0 for no limit).
    """

    tmpdir = _assemble_artifacts(experiment_folder, upload_limit_mb)

    experiment_name, run_name = _user_or_default_names(
        experiment_folder, experiment_name, run_name
    )

    _upload_ml_experiment(
        project_path=project_path,
        experiment_name=experiment_name,
        run_name=run_name,
        artifact_path=pathlib.Path(tmpdir.name),
        parameters=_assemble_parameters(experiment_folder),
        metrics=_assemble_metrics(experiment_folder, metrics),
    )
