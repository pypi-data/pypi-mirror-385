# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Utilities for testing CLI apps."""

import contextlib
import io
import logging
import re
import typing

import click
import click.testing


@contextlib.contextmanager
def stdout_logging(
    logger_name: str = "mednet",
) -> typing.Generator[io.StringIO, None, None]:
    """Collect logging output and returns it as a buffer.

    Parameters
    ----------
    logger_name
        Name of the logger to focus on.

    Yields
    ------
        A buffer with all messages sent to the logging module.
    """

    buf = io.StringIO()
    ch = logging.StreamHandler(buf)
    ch.setFormatter(logging.Formatter("%(message)s"))
    ch.setLevel(logging.INFO)
    logger = logging.getLogger(logger_name)
    logger.addHandler(ch)
    yield buf
    logger.removeHandler(ch)


def assert_exit_0(result: click.testing.Result) -> None:
    """Assert click application exited with code ``0``.

    Parameters
    ----------
    result
        The result to analyze.

    Raises
    ------
    AssertionError
        If the exit code is not zero. Also adds the current output.
    """

    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


def check_help(entry_point: click.Command) -> None:
    """Assert ``--help`` command output works and exit with code ``0``.

    Parameters
    ----------
    entry_point
        The click command to test for.

    Raises
    ------
    AssertionError
        If the exit code is not zero, or if the output does not contain the string
        ``Usage:``.
    """

    runner = click.testing.CliRunner()
    result = runner.invoke(entry_point, ["--help"])
    assert_exit_0(result)
    assert result.output.startswith("Usage:")


def str_counter(substr: str, s: str) -> int:
    """Count number of occurences of regular expression ``str`` on ``s``.

    Parameters
    ----------
    substr
        String or regular expression to search for in ``s``.
    s
        String where to search for ``substr``, that may include new-line characters.

    Returns
    -------
        The count on the number of occurences of ``substr`` on ``s``.
    """

    return sum(1 for _ in re.finditer(substr, s, re.MULTILINE))
