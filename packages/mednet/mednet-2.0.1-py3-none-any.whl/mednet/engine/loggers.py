# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Custom lightning loggers."""

import os
import typing

from lightning.fabric.utilities.types import _PATH
from lightning.pytorch.loggers import TensorBoardLogger


class CustomTensorboardLogger(TensorBoardLogger):
    r"""Custom implementation implementation of lightning's TensorboardLogger.

    This implementation puts all logs inside the same directory, instead of a
    separate "version_n" directories, which is the default lightning behaviour.

    Parameters
    ----------
    save_dir
        Directory where to save the logs to.
    name
        Experiment name. Defaults to ``default``. If it is the empty string
        then no per-experiment subdirectory is used.
    version
        Experiment version. If version is not specified the logger inspects the
        save directory for existing versions, then automatically assigns the
        next available version. If it is a string then it is used as the
        run-specific subdirectory name, otherwise ``version_${version}`` is
        used.
    log_graph
        Adds the computational graph to tensorboard. This requires that the
        user has defined the `self.example_input_array` attribute in their
        model.
    default_hp_metric
        Enables a placeholder metric with key `hp_metric` when
        `log_hyperparams` is called without a metric (otherwise calls to
        log_hyperparams without a metric are ignored).
    prefix
        A string to put at the beginning of metric keys.
    sub_dir
        Sub-directory to group TensorBoard logs. If a sub_dir argument is
        passed then logs are saved in ``/save_dir/name/version/sub_dir/``.
        Defaults to ``None`` in which logs are saved in
        ``/save_dir/name/version/``.
    \**kwargs
        Additional arguments used by :py:class:`tensorboardX.SummaryWriter` can
        be passed as keyword arguments in this logger. To automatically flush
        to disk, ``max_queue`` sets the size of the queue for pending logs before
        flushing. ``flush_secs`` determines how many seconds elapses before
        flushing.
    """

    def __init__(
        self,
        save_dir: _PATH,
        name: str = "lightning-logs",
        version: int | str | None = None,
        log_graph: bool = False,
        default_hp_metric: bool = True,
        prefix: str = "",
        sub_dir: _PATH | None = None,
        **kwargs: dict[str, typing.Any],
    ):
        super().__init__(
            save_dir,
            name,
            version,
            log_graph,
            default_hp_metric,
            prefix,
            sub_dir,
            **kwargs,
        )

    @property
    def log_dir(self) -> str:
        return os.path.join(self.save_dir, self.name)  # noqa: PTH118
