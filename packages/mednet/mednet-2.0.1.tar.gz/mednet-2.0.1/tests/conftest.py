# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import pytest


@pytest.fixture
def datadir(request) -> pathlib.Path:
    """Return the directory in which the test is sitting. Check the pytest
    documentation for more information.

    Parameters
    ----------
    request
        Information of the requesting test function.

    Returns
    -------
    pathlib.Path
        The directory in which the test is sitting.
    """

    return pathlib.Path(request.module.__file__).parents[0] / "data"


def pytest_configure(config):
    """This function is run once for pytest setup.

    Parameters
    ----------
    config
        Configuration values. Check the pytest documentation for more
        information.
    """

    config.addinivalue_line(
        "markers",
        "skip_if_rc_var_not_set(name): this mark skips the test if a certain "
        "~/.config/mednet.toml variable is not set",
    )

    config.addinivalue_line("markers", "slow: this mark indicates slow tests")


def pytest_runtest_setup(item):
    """This function is run for every test candidate in this directory.

    The test is run if this function returns ``None``.  To skip a test,
    call ``pytest.skip()``, specifying a reason.

    Parameters
    ----------
    item
        A test invocation item. Check the pytest documentation for more
        information.
    """

    from mednet.utils.rc import load_rc

    rc = load_rc()

    # iterates over all markers for the item being examined, get the first
    # argument and accumulate these names
    rc_names = [
        mark.args[0] for mark in item.iter_markers(name="skip_if_rc_var_not_set")
    ]

    # checks all names mentioned are set in ~/.config/mednet.toml, otherwise,
    # skip the test
    if rc_names:
        missing = [k for k in rc_names if rc.get(k) is None]
        if any(missing):
            pytest.skip(
                f"Test skipped because {', '.join(missing)} is **not** "
                f"set in ~/.config/mednet.toml",
            )


def rc_variable_set(name):
    from mednet.utils.rc import load_rc

    rc = load_rc()
    pytest.mark.skipif(
        name not in rc,
        reason=f"RC variable '{name}' is not set",
    )


@pytest.fixture(scope="module")
def module_tmp_path(tmp_path_factory) -> pathlib.Path:
    return tmp_path_factory.mktemp("test-cli")
