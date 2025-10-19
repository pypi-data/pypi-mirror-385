.. SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.usage:

=======
 Usage
=======

This package supports a fully reproducible research experimentation cycle for medical
image classification, segmentation, and object detection with support for the following
activities:

* Training: Images are fed to a deep neural network that is trained to match labels
  (classification), reconstruct (segmentation), or find objects (detections)
  automatically, via error back propagation. The objective of this phase is to produce a
  model. We support training on CPU and a few GPU architectures (``cuda`` or ``mps``).
* Prediction (inference): The model is used to generate predictions
* Evaluation: Predictions are used evaluate model performance against provided
  annotations, or visualize prediction results overlayed on the original raw
  images.

We provide :ref:`command-line interfaces (CLI) <mednet.cli>` that implement
each of the functions above.  The commands should be called in sequence to
generate intermediate outputs required for subsequent commands:

.. graphviz:: img/cli-core-light.dot
   :align: center
   :class: only-light

.. graphviz:: img/cli-core-dark.dot
   :align: center
   :class: only-dark
   :caption: Overview of core CLI commands for model training, inference and evaluation. Clicking on each item leads to the appropriate specific documentation. The workflow is the same across different task types (e.g. classification, segmentation or object detection), except for evaluation, that remains task-specific. The right implementation is chosen based on the type of datamodule being used.

The CLI interface is configurable using :ref:`clapper's extensible
configuration framework <clapper.config>`.  In essence, each command-line
option may be provided as a command-line option, or as a variable with the same
name, in a Python file. Each "configuration" file may combine any number of
variables that are pertinent to a CLI application.

.. tip::

   For reproducibility, we recommend you stick to configuration files when
   parameterizing the CLI applications. Notice some of the options in the CLI
   interface (e.g. ``--datamodule``) cannot be passed via the actual
   command-line as it may require complex Python types that cannot be
   synthetized in a single input parameter.

Using our extensible configuration framework, we provide a number of
:py:mod:`Configuration files <mednet.config>` that can be used in one or more
of the activities described in this section. Our command-line framework allows
you to refer to these preset configuration files using special names (a.k.a.
"resources"), that procure and load these for you automatically.

.. _mednet.usage.commands:

Commands
--------

.. toctree::
  :maxdepth: 2

  experiment
  training
  evaluation
  saliency
  segment


.. include:: ../links.rst
