# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Utilities to configure logging for command-line scripts."""

import logging


def setup_cli_logger() -> logging.Logger:
    """Set up the logger to be used for all CLI apps.

    Returns
    -------
        The logger to be used by CLI apps.
    """

    import colorlog
    from clapper.logging import setup

    logger = setup(
        __name__.split(".")[0],
        format="%(levelname)s: %(message)s",
        formatter=colorlog.ColoredFormatter(
            fmt="%(log_color)s[%(levelname)s]%(reset)s %(message)s",
            log_colors={
                "DEBUG": "light_black",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        ),
    )
    logger.setLevel(logging.ERROR)

    return logger
