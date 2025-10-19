.. Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.usage.training:

=======================
 Training and Analysis
=======================

To train a new model, use the command-line interface (CLI) application `mednet
train <../cli.html#mednet-train>`_.  To use this CLI, you must define the input
datamodule that will be used to train the model, as well as the type of model
that will be trained.  You may issue ``mednet train --help`` for a help message
containing more detailed instructions.

For example, to train a model on a pre-configured :ref:`datamodule
<mednet.datamodel>`, run the one of following:

.. code:: sh

   # example classification task
   mednet train -vv pasa montgomery
   # check results in the "results" folder

   # example segmentation task
   mednet train -vv lwnet drive
   # check results in the "results" folder

   # example object detection task
   $ mednet train -vv montgomery-detect faster-rcnn
   # check results in the "results" folder

You may run the system on a GPU by using the ``--device=cuda``, or
``--device=mps``  option.


Plotting training metrics
-------------------------

Various metrics are recorded at each epoch during training, such as the
execution time, loss and resource usage. These are saved in a Tensorboard file,
located in a `logs` subdirectory of the training output folder. This package
provides a `train-analysis <../cli.html#mednet-train-analysis>`_ convenience
CLI that plots the evolution through the training epochs of scalars stored in
log files, and saves them in a PDF file.

To generate a PDF file named ``trainlog.pdf`` with plots showing the evolution
of logged metrics in time, execute the following:

.. code:: sh

   mednet train-analysis -vv -l results/logs


.. include:: ../links.rst
