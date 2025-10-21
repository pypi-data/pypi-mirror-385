.. SPDX-FileCopyrightText: 2025 GFZ Helmholtz Centre for Geosciences
.. SPDX-FileCopyrightText: 2025 Felix Dombrowski
.. SPDX-License-Identifier: EUPL-1.2



================
EnMAP Downloader
================

Downloader for EnMAP data products with STAC


* Free software: EUPL-1.2
* Documentation: https://global-land-monitoring.git-pages.gfz-potsdam.de/enmap_downloader/doc/



Status
======
.. image:: https://git.gfz-potsdam.de/global-land-monitoring/enmap_downloader/badges/main/pipeline.svg
        :target: https://git.gfz-potsdam.de/global-land-monitoring/enmap_downloader/pipelines
        :alt: Pipelines
.. image:: https://git.gfz-potsdam.de/global-land-monitoring/enmap_downloader/badges/main/coverage.svg
        :target: https://global-land-monitoring.git-pages.gfz-potsdam.de/enmap_downloader/coverage/
        :alt: Coverage
.. image:: https://img.shields.io/static/v1?label=Documentation&message=GitLab%20Pages&color=orange
        :target: https://global-land-monitoring.git-pages.gfz-potsdam.de/enmap_downloader/doc/
        :alt: Documentation
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.15784024.svg
        :target: https://zenodo.org/doi/10.5281/zenodo.15784024
        :alt: DOI
.. image:: https://img.shields.io/pypi/v/enmap-downloader.svg
        :target: https://pypi.python.org/pypi/enmap-downloader/
        :alt: PyPi
.. image:: https://static.pepy.tech/badge/enmap-downloader
        :target: https://pepy.tech/projects/enmap-downloader
        :alt: Downloads

See also the latest coverage_ report and the pytest_ HTML report.


Feature overview
================

The EnMAP Downloader is a Python-based tool designed to streamline access to hyperspectral imagery from the Earth Observation Center (EOC).
It provides a flexible and efficient interface for searching, downloading, and preparing EnMAP data tailored to user-defined spatial and temporal criteria.

🌐 **Download Hyperspectral EnMAP Data**

- Fetches .tif hyperspectral datasets (EnMAP L2A) directly from the EOC archive.

🗺️ **User-Defined Spatial Parameters**

- Accepts a a single GeoJSON, or a folder of multiple GeoJSON files — each is handled automatically and clipped to the defined area.

🕒 **User-Defined Temporal Filtering**

- Specify a date range to download only the scenes captured within that timeframe.

⚡ **Multithreaded Downloads**

- Utilizes parallel downloading to significantly speed up large or batch operations on e.g. clusters.

📂 **Batch Processing of Multiple AOIs**

- Efficiently processes multiple areas of interest in one go, especially useful for regional or project-wide data collection.

💾 **Flexible Output Formats**

- Outputs data as GeoTIFFs (.tif) or NumPy arrays (.npy)—choose based on your workflow.

🔐 **Authentication & Config File Support**

- Includes authentication checks and a customizable config file for repeatable, automated use.

✅ **Typical Use Cases**

- 🛰️ Collecting hyperspectral scenes for machine learning and remote sensing projects

- 🗃️ Handling a large folder of AOIs automatically for environmental or urban monitoring

- 🔄 Automating scheduled or repeatable data collection workflows


History / Changelog
===================

You can find the protocol of recent changes in the EnMAP Downloader package
`here <https://git.gfz-potsdam.de/global-land-monitoring/enmap_downloader/-/blob/main/HISTORY.rst>`__.

Credentials
===========

To access the EnMAP data, you need to have a valid EOC account. You can register for an account at the EOC website,
by visiting this `link <https://sso.eoc.dlr.de/geoservice/selfservice/register>`_.
Create your account and verify your email address, after that you need to add the permission to access the EnMAP data.
You can do this by visiting this `page <https://sso.eoc.dlr.de/geoservice/permissions>`_ and subscribing to the
"EnMAP Access Service" permission as seen in the image below.

.. image:: /images/eoc_enmap.png
   :alt: Subscribe to EnMAP Access Service
   :align: center

After that your account is properly set up and you can use the package.

When running the code for the first time, a .env file will be created in the root directory of the package.
This file will contain the following variables:

.. code-block:: bash

    ENMAP_USERNAME=USERNAME
    ENMAP_PASSWORD=PASSWORD

You can edit this file to securely add your EOC credentials. The package will automatically read the credentials from this file when executing the code.

**Important:** This file contains sensitive information. To protect your credentials, keep it private and do not share it with others.

The package requires valid credentials to function properly. If the credentials are missing or incorrect, you will receive an error message.

Once saved, your credentials will be stored in the ``.netrc`` file in your home directory. This means you won’t need to enter them again for future runs.


Quick Installation
==================

To install the package, clone it into a local directory and run the following command:

.. code-block:: bash

    python -m pip install .

Alternatively you can create a conda environment and install the package with its dependencies:

.. code-block:: bash

    conda env create -f environment_enmap_downloader.yml
    conda activate enmap_downloader
    pip install .

Make sure to create a config.json file in the config directory. You can use the provided example file as a template.
The config.json file should contain the following information:

.. code-block:: json

    {
    "search_settings": {
        "collections": [
        "ENMAP_HSI_L2A"
        ],
        "catalog_link" : "https://geoservice.dlr.de/eoc/ogc/stac/v1/",
        "aoi_settings": {
            "geojson": "./config/geojson",
            "start_date": "",
            "end_date": ""
        }
    },
    "result_settings": {
        "crop_value" : "bbox",
        "results_dir": "./downloads",
        "result_format": "tif",
        "download_data": true,
        "download_metadata": true,
        "logging_level": "INFO",
        "logging_dir": "./logs"
    }


Configuration Options
=====================

Below is a description of the configurable parameters in the configuration file used by this project.

AOI Settings
------------

These settings define the area of interest (AOI) and the time window for data selection.

.. code-block:: json

    "aoi_settings": {
        "geojson": "./config/geojson",
        "start_date": "",
        "end_date": ""
    }

- **geojson** (`str`):
  Path to a GeoJSON file that defines the spatial parameters for the area of interest.

- **start_date** (`str`, optional):
  Start date for the data query, in `YYYY-MM-DD` format. Leave empty to ignore.

- **end_date** (`str`, optional):
  End date for the data query, in `YYYY-MM-DD` format. Leave empty to ignore.

Result Settings
---------------

These settings control how the results are processed, saved, and logged.

.. code-block:: json

    "result_settings": {
        "crop_value" : "bbox",
        "results_dir": "./downloads",
        "result_format": "tif",
        "download_data": true,
        "download_metadata": true,
        "logging_level": "INFO",
        "logging_dir": "./logs"
    }

- **crop_value** (`str`):

  - If `default`, the data will not be cropped.
  - If `bbox`, the data will be cropped to the max bounds of the supplied geojson.
  - If `precise`, the data will be cropped to the exact polygon of the supplied geojson.

.. image:: /images/cropping.png
   :alt: Example of cropping
   :width: 150px
   :align: center

- **results_dir** (`str`):
  Directory path where result files will be saved.

- **result_format** (`str`):
  Format in which results are stored. Supported options: `"npy"` (NumPy array), `"tif"` (GeoTIFF).

- **download_data** (`bool`):
  If `true`, the raw data will be downloaded, in the defined `result_format`.

- **download_metadata** (`bool`):
  If `true`, associated metadata files will also be downloaded.

- **logging_level** (`str`):
  Logging verbosity level. Typical values: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`.

- **logging_dir** (`str`):
  Directory where log files are saved.

Then you can use the package by running the following code block:

.. code-block:: python

    import os

    from enmap_downloader.config import loadConfiguration, Config
    from enmap_downloader.enmap_downloader import enmapDownloader

    if __name__ == "__main__":

        config_file = os.path.abspath("config/config.json")
        config = loadConfiguration(path=config_file)
        Config(**config)

        enmapDownloader(config, in_parallel=True)

The function enmapDownloader has the following parameters:

- **config** (`Config`): The configuration object containing all settings.

- **in_parallel** (`bool`, optional): If `True`, the downloader will run in parallel mode, downloading multiple files simultaneously. Default is `True`.

- **num_workers** (`int`, optional): Number of worker threads used by the `ThreadPoolExecutor <https://docs.python.org/3/library/concurrent.futures.html>`_ when `in_parallel` is `True`. Default is `None`, which uses the number of available CPU cores.

- **limit** (`int`, optional): Maximum number of items to download per query. If `None`, all items matching the query will be downloaded. Default is `None`.

The downloader will search for EnMAP data products based on the configuration provided, download the data, and save it in the specified format and directory. The downloaded files will be logged in the specified logging directory.

Jupyer Notebooks
================

To make it easier for new users, or anyone who wants to try out the package quickly, we provide a collection of Jupyter notebooks.
These notebooks demonstrate a variety of common use cases and are designed to run out-of-the-box, with only the need for small adjustments.
Each notebook contains step-by-step examples that can be executed interactively. This makes them well suited both for first explorations and for adapting the workflows to your own data or research questions.
If you are new to the package, starting with the notebooks is the fastest way to get familiar with its core functionality.

FAQ
===

- Is there a possibility to just fetch the available data with given AOI and time range without downloading the data?

Yes, you can set the `fetch_only` parameter to `True` in the `enmapDownloader` function. This will only fetch the available data without downloading it.

- When running the downloader, I am getting the error message "Error 403: Forbidden". What can I do?

This error message indicates that your credentials are not correct or you do not have the permission to access the EnMAP data.
Please make sure that you have a valid EOC account and that you have subscribed to the "EnMAP Access Service" permission as described in the Credentials section above.
It may take some time until the permission is activated.
The downloader reads the credentials from the .env file, which is located in your home directory. Please make sure that the credentials are correct and that the .env file is in the correct location.
If all of this is correct, there might also be a problem with your username / password. The .netrc file only allows some special characters in the password.
Try to especially avoid the following characters: \ and #.

Developed by
============

enmap_downloader has been developed by the `Global Land Monitoring <https://www.gfz.de/en/section/remote-sensing-and-geoinformatics/topics/global-land-monitoring>`_ group and `FERN.Lab <https://fernlab.gfz-potsdam.de/>`_ at the `GFZ Helmholtz Centre for Geosciences <https://www.gfz.de/en/>`_.

Copyright
=========

Copyright (c) 2025 GFZ Helmholtz Centre for Geosciences.

Credits
=======

This package was created with Cookiecutter_ and the `fernlab/cookiecutter-py-package`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`fernlab/cookiecutter-py-package`: https://github.com/fernlab/cookiecutter-py-package
.. _coverage: https://global-land-monitoring.git-pages.gfz-potsdam.de/enmap_downloader/coverage/
.. _pytest: https://global-land-monitoring.git-pages.gfz-potsdam.de/enmap_downloader/test_reports/report.html
