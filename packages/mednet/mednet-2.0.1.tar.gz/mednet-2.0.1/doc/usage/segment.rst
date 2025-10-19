.. Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.usage.segment:

======================================================
 Annotation visualisation and analysis (segmentation)
======================================================

The evaluation of segmentation system offer more options that those for
classification systems, allowing further analysis to be carried out on
segmentation datamodules.  In particular, this package supports inter-annotator
comparison analysis for segmentation tasks.  This guide describes the workflow
required to implement it for suitable datamodules.

The command-line interface for annotation visualisation and analysis is
available through the `mednet segment <../cli.html#mednet-segment>`_
subcommands. The commands should be called in sequence to generate intermediate
outputs required for subsequent commands:

.. graphviz:: img/cli-segment-light.dot
   :align: center
   :class: only-light

.. graphviz:: img/cli-segment-dark.dot
   :align: center
   :class: only-dark
   :caption: Overview of CLI commands for annotation analysis. Clicking on each item leads to the appropriate specific documentation.


Dumping Annotations
-------------------

The evaluation of segmentation systems can compare results obtained for each of
the datamodule splits, by a pre-trained model, to those of another annotator.
This allows benchmarking human against machine on the same segmentation task.

So that the evaluation script can input alternate annotator data, it must be
converted from its raw representation into a format similar to those used by
the prediction step.

Annotations can be dumped with the `segment dump-annotations
<../cli.html#mednet-segment-dump-annotations>`_ command. For example:

.. code:: sh

   mednet segment dump-annotations -vv lwnet drive-2nd --output-folder=results

The name of a datamodule including the annotations for interest must be
provided.  Many, but not all, supported databases do contain alternate
annotations that can be useful in this step.  The model configuration is input
to ensure model transforms applied to the common processing pipeline are also
applied while dumping alternate annotations.


Evaluation
----------

Whilst basic evaluation is carried out during experiment running, it is
possible to explicitly call the specialized segmentation evaluation command to
add comparison to the performance of human annotators.

Segmentation evaluation can be run with the `segment evaluate
<../cli.html#mednet-segment-evaluate>`_ command. For example:

.. code:: sh

   mednet segment evaluate -vv --predictions=path/to/predictions.json --compare-annotator=path/to/annotations.json --output-folder=results


Prediction Visualization
------------------------

Finally, it is sometimes useful to generate visualisations of manually, or
automatically generated annotations.  Annotation visualisations can be
generated standalone, overlayed in the original image, or displaying true/false
positives/negatives.  To do so, use the `segment view
<../cli.html#mednet-segment-view>`_ command. For example:


.. code:: sh

   # use fixed threshold on 0.5 to generate visualisations
   mednet segment view -vv --predictions=path/to/predictions.json --output-folder=results

   # use threshold maximum f1-score at validation set to generate visualisations
   mednet segment view -vv --threshold=validation --predictions=path/to/predictions.json --output-folder=results

.. include:: ../links.rst
