.. Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.usage.saliency:

===================================================
 Saliency Generation and Analysis (classification)
===================================================

A saliency map highlights areas of interest within an image, that contributed
to the produced score. For example, in the context of tuberculosis detection
from chest X-ray images, this would be the locations in those images where
tuberculosis is (supposedly) present.

This package provides scripts that can generate saliency maps and compute
relevant metrics for evaluating the performance of saliency map algorithms
taking into consideraton result completeness, and human interpretability.
Result completeness evaluates how much of the output score is explained by the
computed saliency maps.  Human interpretability evaluates how much of the
generated saliency map matches human expectations when performing the same
task.

Evaluation of human interpretability obviously requires the use of a datamodule
with human-annotated saliency information that is supposed to correlate with
image labels.

The command-line interface for saliency map generation and analysis is
available through the `mednet classify saliency
<../cli.html#mednet-classify-saliency>`_ subcommands. The commands should be
called in sequence to generate intermediate outputs required for subsequent
commands:

.. graphviz:: img/cli-saliency-light.dot
   :align: center
   :class: only-light

.. graphviz:: img/cli-saliency-dark.dot
   :align: center
   :class: only-dark
   :caption: Overview of CLI commands for saliency generation and evaluation. Clicking on each item leads to the appropriate specific documentation. Saliency generation can be done for any datamodule split.  In this figure, only the Test data set is displayed for illustrative purposes.


Saliency Generation
-------------------

Saliency maps can be generated with the `saliency generate
<../cli.html#mednet-classify-saliency-generate>`_ command. They are represented
as numpy arrays of the same size as thes images, with values in the range [0-1]
and saved in ``.npy`` files.

Several saliency mapping algorithms are available to choose from, which can be
specified with the ``-s`` option.  The default algorithm is GradCAM.

To generate saliency maps for all splits in a datamodule, run a command such
as:

.. code:: sh

   mednet classify saliency generate -vv pasa tbx11k-v1-healthy-vs-atb --weight=path/to/model-at-lowest-validation-loss.ckpt --output-folder=results


Viewing
-------

To overlay saliency maps over the original images, use the `saliency view
<../cli.html#mednet-classify-saliency-view>`_ command. Results are saved as PNG
images in which brigter pixels correspond to areas with higher saliency.

To generate visualizations, run a command such as:

.. code:: sh

   # input-folder is the location of the saliency maps created as per above
   mednet classify saliency view -vv pasa tbx11k-v1-healthy-vs-atb --input-folder=input-folder --output-folder=results


Completeness
------------

The saliency completeness script computes ROAD scores of saliency maps and saves them in
a JSON file. The ROAD algorithm :cite:p:`rong_consistent_2022` estimates the
explainability (in the completeness sense) of saliency maps by substituting relevant
pixels in the input image by a local average, re-running prediction on the altered
image, and measuring changes in the output classification score when said perturbations
are in place. By substituting most or least relevant pixels with surrounding averages,
the ROAD algorithm estimates the importance of such elements in the produced saliency
map.

To run completeness analysis for a given model and saliency-map algorithm on
all splits of a datamodule, use the `saliency completeness
<../cli.html#mednet-classify-saliency-completeness>`_ command. ROAD scores for
each input sample are computed and stored in a JSON file for later analysis.
For example:

.. code:: sh

   mednet classify saliency completeness -vv pasa tbx11k-v1-healthy-vs-atb --device="cuda:0" --weight=path/to/model-at-lowest-validation-loss.ckpt --output-folder=results

.. note::

   1. Running the completness analysis on a GPU is strongly advised.  The
      algorithm requires multiple model passes per sample.
   2. The target datamodule does NOT require specific annotations for this
      analysis


Interpretability
----------------

Given a target label, the interpretability step computes the proportional
energy and average saliency focus in a datamodule. The proportional energy is
defined as the quantity of activation that lies within the ground truth boxes
compared to the total sum of the activations. The average saliency focus is the
sum of the values of the saliency map over the ground-truth bounding boxes,
normalized by the total area covered by all ground-truth bounding boxes.

To run interpretability analysis for a given model and saliency-map algorithm
on all splits of a datamodule, use the `saliency interpretability
<../cli.html#mednet-classify-saliency-interpretability>`_ command. The average
egnery and saliency focus features for each input sample are computed and
stored in a JSON file for later analysis. For example:

.. code:: sh

   mednet saliency interpretability -vv tbx11k-v1-healthy-vs-atb --input-folder=parent-folder/saliencies/ --output-json=path/to/interpretability-scores.json


.. note::

   Currently, this functionality requires a datamodule containing
   human-annotated bounding boxes.


.. include:: ../links.rst
