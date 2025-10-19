.. Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.experiment:

==============================
 Running complete experiments
==============================

We provide an `experiment command <../cli.html#mednet-experiment>`_ that runs
training, followed by prediction and evaluation. After running, you will be
able to find results from model fitting, prediction and evaluation under a
single output directory.

For example, to train a model on a pre-configured :ref:`datamodule
<mednet.datamodel>` evaluate its performance, outputting predictions and
performance curves, run the one of following:

.. code:: sh

   # example classification task using the "pasa" network model
   # on the "montgomery" datamodule
   $ mednet experiment -vv pasa montgomery
   # check results in the "results" folder

   # example semantic sementation task using the "lwnet" network model
   # on the "drive" datamodule
   $ mednet experiment -vv lwnet drive
   # check results in the "results" folder

   # example object detection task using the "faster-rcnn" network model
   # on the "montgomery" (for object detection) datamodule
   $ mednet experiment -vv montgomery-detect faster-rcnn
   # check results in the "results" folder

You may run the system on a GPU by using the ``--device=cuda``, or
``--device=mps``  option.


.. include:: ../links.rst
