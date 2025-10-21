.. SPDX-FileCopyrightText: 2025 GFZ Helmholtz Centre for Geosciences
.. SPDX-FileCopyrightText: 2025 Felix Dombrowski
.. SPDX-License-Identifier: EUPL-1.2



.. _installation:

============
Installation
============

Using pip
---------

EnMAP Downloader can be installed using pip_ (latest version recommended) as follows:

1. Clone the EnMAP Downloader source code:

   .. code-block:: bash

    $ git clone git@git.gfz-potsdam.de:global-land-monitoring/enmap_downloader.git
    $ cd enmap_downloader

2. Create a virtual environment for EnMAP Downloader and install all dependencies from the requirements.txt file and install EnMAP Downloader itself:

    .. code-block:: bash

     $ python -m venv venv
     $ source venv/bin/activate
     $ pip install .

Using Anaconda or Miniconda
---------------------------

Using mamba_ (latest version recommended), EnMAP Downloader is installed as follows:

1. Clone the EnMAP Downloader source code:

   .. code-block:: bash

    $ git clone git@git.gfz-potsdam.de:global-land-monitoring/enmap_downloader.git
    $ cd enmap_downloader


2. Create virtual environment for enmap_downloader and install all dependencies from the environment_enmap_downloader.yml file and install EnMAP Downloader itself:

   .. code-block:: bash

    $ conda env create -f environment_enmap_downloader.yml
    $ conda activate enmap_downloader
    $ pip install .


This is the preferred method to install EnMAP Downloader, as it always installs the most recent stable release and
automatically resolves all the dependencies.

.. note::

    EnMAP Downloader has been tested with Python 3.12+., i.e., should be fully compatible to all Python versions from 3.12 onwards.


.. _pip: https://pip.pypa.io
.. _Python installation guide: https://docs.python-guide.org/starting/installation/
.. _conda: https://conda.io/docs
.. _mamba: https://github.com/mamba-org/mamba
