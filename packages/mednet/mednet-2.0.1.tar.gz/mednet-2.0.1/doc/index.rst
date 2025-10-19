.. SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet:

==============================================================================
 Multi-task Library to Develop Computer-Aided Tools for Medical Data Analysis
==============================================================================

.. todolist::

Framework for development and analysis of deep neural network architectures
applied to medical data (images, 2D and 3D). This package can be readily used
on a number of public datasets.  It can be extended to add more datasets, and
models.

Use one or more the BibTeX references below to cite this work:

.. code:: bibtex

    @misc{guler_2024,
        title     = {Refining {Tuberculosis} {Detection} in {CXR} {Imaging}: {Addressing} {Bias} in {Deep} {Neural} {Networks} via {Interpretability}},
        url       = {http://arxiv.org/abs/2407.14064},
        publisher = {arXiv},
        author    = {Güler, Özgür Acar and Günther, Manuel and Anjos, André},
        month     = jul,
        year      = {2024},
        note      = {arXiv:2407.14064 [cs]},
        annote    = {Comment: Preprint of paper presented at EUVIP 2024},
    }

   @misc{laibacher_2019,
       title         = {On the Evaluation and Real-World Usage Scenarios of Deep Vessel Segmentation for Retinography},
       author        = {Tim Laibacher and Andr\'e Anjos},
       year          = {2019},
       eprint        = {1909.03856},
       archivePrefix = {arXiv},
       primaryClass  = {cs.CV},
       url           = {https://arxiv.org/abs/1909.03856},
   }


User Guide
----------

.. toctree::
   :maxdepth: 2

   install
   usage/index
   baselines
   data-model
   databases/index
   models
   cli
   api
   config
   contribute
   bibliography


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. include:: links.rst
