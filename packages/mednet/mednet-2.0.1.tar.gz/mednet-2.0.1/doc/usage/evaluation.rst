.. Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.usage.evaluation:

===========================
 Prediction and Evaluation
===========================

This guide explains how to run prediction (inference) or a complete evaluation
using command-line tools.  Inference produces network model outputs for input
images, while evaluation will analyze such outputs against existing annotations
and produce performance figures.


Prediction
----------

In prediction (or inference) mode, we input a model, a datamodule, and a
pre-trained set of weights (a.k.a. "checkpoint") generated during training, and
output a JSON file containing the prediction outputs for every input image.

To run inference, use the sub-command `mednet predict
<../cli.html#mednet-predict>`_


For example, to generate predictions for a pre-trained model on a
pre-configured :ref:`datamodule <mednet.datamodel>`, run the one of following:

.. code:: sh

   # example for a classification task
   mednet predict -vv pasa montgomery --weight=<results/model.ckpt> --output-folder=predictions

   # example for a segmentation task
   mednet predict -vv lwnet drive --weight=<results/model.ckpt> --output-folder=predictions

   # example for a object detection task
   mednet predict -vv faster-rcnn montgomery-detect --weight=<results/model.ckpt> --output-folder=predictions


Replace ``<results/model.ckpt>`` to a path leading to the pre-trained model.

You may run the system on a GPU by using the ``--device=cuda``, or
``--device=mps``  option.


Evaluation
----------

In evaluation, we input predictions to generate performance summaries that help
analysis of a trained model. The generated files are a PDF containing various
plots and a table of metrics for each datamodule split. Evaluation is done
using either `mednet classify evaluate <../cli.html#mednet-classify-evaluate>`_
or `mednet segment evaluate <../cli.html#mednet-segment-evaluate>`_ by passing
the JSON file generated during the prediction step.

.. note::

   Evaluation is task-specific and behaves slightly different for e.g.
   classification or segmentation tasks.  The common "experiment" CLI will call
   the appropriate evaluation script depending on the provided datamodule
   configuration.

To run evaluation on predictions generated in the prediction step, do one of
the following:

.. code:: sh

   # classification task
   mednet classify evaluate -vv --predictions=path/to/predictions.json

   # segmentation task
   mednet segment evaluate -vv --predictions=path/to/predictions.json

   # object detection task
   mednet detect evaluate -vv --predictions=path/to/predictions.json


.. include:: ../links.rst
