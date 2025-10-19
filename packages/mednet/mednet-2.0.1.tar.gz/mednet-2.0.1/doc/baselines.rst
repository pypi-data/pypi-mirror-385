.. SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.baselines:

==================================
 Baselines and Pre-trained Models
==================================

We maintain a set of `baseline results <baseline-experiments_>`_ for a few
specific configurations, to serve as the basis of comparison between various
installations, and to give a sense of expected performance for built-in
configurations.  For each configuration, it is possible to access performance
figures (as tables and plots), metadata (including the package version used),
as well as a re-usable model file.


.. _mednet.baselines.classify:

Classification baselines
------------------------

.. list-table::

   * - Database Config.
     - Model Config.
     - Link
   * - :py:mod:`shenzhen <mednet.config.classify.data.shenzhen.default>`
     - :py:mod:`pasa <mednet.config.classify.models.pasa>`
     - https://gitlab.idiap.ch/medai/software/mednet/-/ml/experiments/42
   * - :py:mod:`montgomery-shenzhen-indian-tbx11k-v1 <mednet.config.classify.data.montgomery_shenzhen_indian_tbx11k.v1_healthy_vs_atb>`
     - :py:mod:`pasa <mednet.config.classify.models.pasa>`
     - https://gitlab.idiap.ch/medai/software/mednet/-/ml/experiments/41
   * - :py:mod:`shenzhen <mednet.config.classify.data.shenzhen.default>`
     - :py:mod:`densenet <mednet.config.classify.models.densenet>`
     - https://gitlab.idiap.ch/medai/software/mednet/-/ml/experiments/39
   * - :py:mod:`montgomery-shenzhen-indian-tbx11k-v1 <mednet.config.classify.data.montgomery_shenzhen_indian_tbx11k.v1_healthy_vs_atb>`
     - :py:mod:`densenet <mednet.config.classify.models.densenet>`
     - https://gitlab.idiap.ch/medai/software/mednet/-/ml/experiments/40


.. include:: links.rst
