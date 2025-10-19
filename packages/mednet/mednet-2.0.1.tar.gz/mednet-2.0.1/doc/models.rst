.. SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.models:

=====================
 Model Architectures
=====================

Deep-neural network models are categorized by tasks.


.. _mednet.models.classify:

Classification
--------------

Pre-configured models supporting classification tasks.

.. list-table:: Pre-configured classification models.
   :align: left

   * - Config. key
     - Module
     - Base type
   * - ``alexnet``
     - :py:mod:`.config.classify.models.alexnet`
     - :py:class:`.models.classify.alexnet.Alexnet`
   * - ``alexnet-pretrained``
     - :py:mod:`.config.classify.models.alexnet_pretrained`
     - :py:class:`.models.classify.alexnet.Alexnet`
   * - ``cnn3d``
     - :py:mod:`.config.classify.models.cnn3d`
     - :py:class:`.models.classify.cnn3d.Conv3DNet`
   * - ``densenet``
     - :py:mod:`.config.classify.models.densenet`
     - :py:class:`.models.classify.densenet.Densenet`
   * - ``densenet-pretrained``
     - :py:mod:`.config.classify.models.densenet_pretrained`
     - :py:class:`.models.classify.densenet.Densenet`
   * - ``logistic-regression``
     - :py:mod:`.config.classify.models.logistic_regression`
     - :py:class:`.models.classify.logistic_regression.LogisticRegression`
   * - ``mlp``
     - :py:mod:`.config.classify.models.mlp`
     - :py:class:`.models.classify.mlp.MultiLayerPerceptron`
   * - ``pasa``
     - :py:mod:`.config.classify.models.pasa`
     - :py:class:`.models.classify.pasa.Pasa`
   * - ``vit-large``
     - :py:mod:`.config.classify.models.vit_large`
     - :py:class:`.models.classify.vit.ViT`
   * - ``vit-small``
     - :py:mod:`.config.classify.models.vit_small`
     - :py:class:`.models.classify.vit.ViT`
   * - ``vit-large-lora``
     - :py:mod:`.config.classify.models.vit_large_lora`
     - :py:class:`.models.classify.vit.ViT`
   * - ``vit-small-lora``
     - :py:mod:`.config.classify.models.vit_small_lora`
     - :py:class:`.models.classify.vit.ViT`


.. _mednet.models.segment:

Semantic Segmentation
---------------------

Pre-configured models supporting semantic segmentation tasks.

.. list-table:: Pre-configured semantic segmentation models
   :align: left

   * - Config. key
     - Module
     - Base type
   * - ``driu``
     - :py:mod:`.config.segment.models.driu`
     - :py:class:`.models.segment.driu.DRIU`
   * - ``driu-bn``
     - :py:mod:`.config.segment.models.driu_bn`
     - :py:class:`.models.segment.driu_bn.DRIUBN`
   * - ``driu-od``
     - :py:mod:`.config.segment.models.driu_od`
     - :py:class:`.models.segment.driu_od.DRIUOD`
   * - ``driu-pix``
     - :py:mod:`.config.segment.models.driu_pix`
     - :py:class:`.models.segment.driu_pix.DRIUPix`
   * - ``hed``
     - :py:mod:`.config.segment.models.hed`
     - :py:class:`.models.segment.hed.HED`
   * - ``lwnet``
     - :py:mod:`.config.segment.models.lwnet`
     - :py:class:`.models.segment.lwnet.LittleWNet`
   * - ``m2unet``
     - :py:mod:`.config.segment.models.m2unet`
     - :py:class:`.models.segment.m2unet.M2Unet`
   * - ``unet``
     - :py:mod:`.config.segment.models.unet`
     - :py:class:`.models.segment.unet.Unet`


.. _mednet.models.detect:

Object Detection
----------------

Pre-configured models supporting object detection tasks.

.. list-table:: Pre-configured object detection models
   :align: left

   * - Config. key
     - Module
     - Base type
   * - ``faster-rcnn``
     - :py:mod:`.config.detect.models.faster_rcnn`
     - :py:class:`.models.detect.faster_rcnn.FasterRCNN`


.. include:: links.rst
