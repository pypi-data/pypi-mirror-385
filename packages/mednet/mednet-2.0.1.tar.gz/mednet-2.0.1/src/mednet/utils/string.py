# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""String manipulation utilities."""


def rewrap(s: str) -> str:
    """Re-wrap input string to remove all whitespaces.

    This function will transform all whitespaces (one or more spaces, tabs, newlines,
    returns, formfeeds) into a single space on a given string.

    Parameters
    ----------
    s
        The input string.

    Returns
    -------
        The "re-wrapped" string with multiple whitespaces transformed to a single space.
    """
    return " ".join(s.split())
