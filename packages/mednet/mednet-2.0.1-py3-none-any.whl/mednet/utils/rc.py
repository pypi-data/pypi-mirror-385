# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from clapper.rc import UserDefaults


def load_rc() -> UserDefaults:
    """Return global configuration variables.

    Returns
    -------
        The user defaults read from the user .toml configuration file.
    """
    return UserDefaults("mednet.toml")
