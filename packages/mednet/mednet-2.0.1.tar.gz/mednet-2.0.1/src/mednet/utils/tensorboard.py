# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

from tensorboard.backend.event_processing.event_accumulator import (
    EventAccumulator,
)


def scalars_to_dict(
    logdir: pathlib.Path,
) -> dict[str, tuple[list[int], list[float]]]:
    """Return scalars stored in tensorboard event files.

    This method will gather all tensorboard event files produced by a training
    run, and will return a dictionary with all collected scalars, ready for
    plotting.

    Parameters
    ----------
    logdir
        Directory containing the event files.

    Returns
    -------
    dict[str, tuple[list[int], list[float]]]
        A dictionary where keys represent all scalar names, and values
        correspond to a tuple that contains an array with epoch numbers (when
        values were taken), when the monitored values themselves.  The lists
        are pre-sorted by epoch number.
    """

    retval: dict[str, tuple[list[int], list[float]]] = {}

    for logfile in sorted(logdir.glob("events.out.tfevents.*")):
        event_accumulator = EventAccumulator(str(logfile))
        event_accumulator.Reload()

        for tag in event_accumulator.Tags()["scalars"]:
            steps, values = retval.setdefault(tag, ([], []))
            for data_point in event_accumulator.Scalars(tag):
                steps.append(data_point.step)
                values.append(data_point.value)

    # reorder according to step number
    for key, (steps, values) in retval.items():
        _steps, _values = zip(*sorted(zip(steps, values)))
        retval[key] = (list(_steps), list(_values))  # type: ignore

    return retval
