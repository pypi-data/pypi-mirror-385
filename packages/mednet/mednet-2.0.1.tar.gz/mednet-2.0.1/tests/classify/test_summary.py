# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import mednet.config.classify.models.pasa as pasa_config
from mednet.utils.summary import summary


def test_summary_pasa():
    model = pasa_config.model
    s, param = summary(model)
    assert isinstance(s, str)
    assert isinstance(param, int)
