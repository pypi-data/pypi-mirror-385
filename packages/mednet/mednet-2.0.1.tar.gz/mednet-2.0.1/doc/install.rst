.. SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.install:

==============
 Installation
==============

Installation may follow one of three paths: deployment or development for
CPU-only execution, or a mixed development and deployment environment with
Nvidia CUDA support. Choose the relevant tab for details on each of those
installation paths.

.. tab:: Deployment

   Install using uv_, or your preferred Python project management solution:

   **Stable** release, from PyPI:

   .. code:: sh

      uv pip install mednet
      mednet info

   **Latest** development branch, from its git repository:

   .. code:: sh

      uv pip install git+https://gitlab.idiap.ch/medai/software/mednet@main
      mednet info


.. tab:: Development

   Checkout the repository, and then use pixi_ to setup a full development
   environment:

   .. code:: sh

      git clone git@gitlab.idiap.ch:medai/software/mednet
      pixi install --frozen
      pixi run mednet info

   .. tip::

      The ``--frozen`` flag will ensure that the latest lock-file available
      with sources is used.  If you'd like to update the lock-file to the
      latest set of compatible dependencies, remove that option.

      If you use `direnv to setup your pixi environment
      <https://pixi.sh/latest/features/environment/#using-pixi-with-direnv>`_
      when you enter the directory containing this package, you can use a
      ``.envrc`` file similar to this:

      .. code:: sh

         watch_file pixi.lock
         export PIXI_FROZEN="true"
         eval "$(pixi shell-hook)"


.. tab:: CUDA

   Checkout the repository, and then use pixi_ to setup a version of this
   package that can run on a CUDA-enabled machine:

   .. code:: sh

      git clone git@gitlab.idiap.ch:medai/software/mednet
      pixi install --frozen -e cuda
      pixi run -e cuda mednet info

   To enable CUDA support, always run applications using the ``cuda``
   environment via ``pixi run -e cuda ...``.  Refer to further pixi
   configuration tips on the *Development* tab above.


.. _mednet.setup:

Setup
-----

A global configuration file sets up global package options.  For this package,
most options concern the leading paths to supported :ref:`databases
<mednet.datamodel>`. The location of the configuration file depends on the
value of the environment variable ``$XDG_CONFIG_HOME``, but defaults to
``~/.config/mednet.toml`` in Unix-like systems (Linux and macOS).  You may edit
this file using your preferred editor.

Here is an example configuration file that may be useful as a starting point,
describing the variable names for most supported databases:

.. code:: toml

   [datadir]

   # classification
   hivtb = "/Users/myself/dbs/hiv-tb"
   indian = "/Users/myself/dbs/tbxpredict"
   tbpoc = "/Users/myself/dbs/tb-poc"
   tbx11k = "/Users/myself/dbs/tbx11k"

   # segmentation
   chasedb1 = "/Users/myself/dbs/chase-db1"
   drive = "/Users/myself/dbs/drive"
   hrf = "/Users/myself/dbs/hrf"
   iostar = "/Users/myself/dbs/iostar/IOSTAR Vessel Segmentation Dataset"
   stare = "/Users/myself/dbs/stare"
   refuge = "/Users/myself/dbs/refuge"
   drishtigs1 = "/Users/myself/dbs/drishtigs1"
   rimoner3 = "/Users/myself/dbs/rimone/RIM-ONE r3"
   drionsdb = "/Users/myself/dbs/drionsdb"
   jsrt = "/Users/myself/dbs/jsrt"

   # classification and segmentation
   montgomery = "/Users/myself/dbs/montgomery-xrayset"
   shenzhen = "/Users/myself/dbs/shenzhen"
   cxr8 = "/Users/myself/dbs/cxr8-256px"

   [cxr8]
   idiap_folder_structure = false  # set to `true` if at Idiap


While most supported datbases are listed above, you can get an up-to-date list
of supported databases (and their types) using the command `database list
<../cli.html#mednet-database-list>`_:

.. code:: sh

   mednet database list
     - hivtb (mednet.config.classify.data.hivtb): /Users/myself/dbs/hiv-tb
     - indian (mednet.config.classify.data.indian): /Users/myself/dbs/tbxpredict
     - montgomery (mednet.config.classify.data.montgomery, mednet.config.segment.data.montgomery): /Users/myself/dbs/montgomery-preprocessed
     - nih_cxr14 (mednet.config.classify.data.nih_cxr14): /Users/myself/dbs/cxr8-256px
     - padchest (mednet.config.classify.data.padchest): NOT installed
     - shenzhen (mednet.config.classify.data.shenzhen, mednet.config.segment.data.shenzhen): /Users/myself/dbs/shenzhen
     - tbpoc (mednet.config.classify.data.tbpoc): /Users/myself/dbs/tb-poc
     - tbx11k (mednet.config.classify.data.tbx11k): /Users/myself/dbs/tbx11k
     - visceral (mednet.config.classify.data.visceral): NOT installed
     - avdrive (mednet.config.segment.data.avdrive): NOT installed
     - chasedb1 (mednet.config.segment.data.chasedb1): /Users/myself/dbs/chase-db1
     - cxr8 (mednet.config.segment.data.cxr8): /Users/myself/dbs/cxr8-256px
     - drhagis (mednet.config.segment.data.drhagis): NOT installed
     - drionsdb (mednet.config.segment.data.drionsdb): /Users/myself/dbs/drionsdb
     - drishtigs1 (mednet.config.segment.data.drishtigs1): /Users/myself/dbs/drishtigs1
     - drive (mednet.config.segment.data.drive): /Users/myself/dbs/drive
     - hrf (mednet.config.segment.data.hrf): /Users/myself/dbs/hrf
     - iostar (mednet.config.segment.data.iostar): /Users/myself/dbs/iostar/IOSTAR Vessel Segmentation Dataset
     - jsrt (mednet.config.segment.data.jsrt): /Users/myself/dbs/jsrt
     - refuge (mednet.config.segment.data.refuge): /Users/myself/dbs/refuge
     - rimoner3 (mednet.config.segment.data.rimoner3): /Users/myself/dbs/rimone/RIM-ONE r3
     - stare (mednet.config.segment.data.stare): /Users/myself/dbs/stare

Classification databases are implemented inside the submodule
:py:mod:`mednet.data.classify`, while segmentation databases are inside
:py:mod:`mednet.data.segment`.  Databases that support both classification and
segmentation tasks have implementations on both submodules.

.. note::

   You must procure and download databases yourself.  **Raw data is not
   included in this package as we are not authorised to redistribute it**.

   To check whether the downloaded version is consistent with the structure
   that is expected by this package, use the command `database check
   <../cli.html#mednet-database-check>`:

   .. code:: sh

      mednet database check <database_name>

Each database may be split in different train, validation and test subsets,
through a :ref:`DatabaseSplit <mednet.datamodel>`, and wrapped in a separate
:ref:`DataModule <mednet.datamodel>`.  To list all pre-configured splits (i.e.
data modules), use the command `config list <../cli.html#mednet-config-list>`_,
and search for modules starting with `mednet.config.classify.data` or
`mednet.config.segment.data` depending on the type of task you are interested
on.

A list of out-of-the-box supported data modules for :ref:`classification
<mednet.databases.classify>` or :ref:`segmentation <mednet.databases.segment>`
is available in this guide.


.. include:: links.rst
