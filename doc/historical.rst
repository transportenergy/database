Historical & statistical data (:mod:`item.historical`)
******************************************************

This module contains the code that implements the `iTEM Open Data project <https://transportenergy.org/data/historical/>`_, the broader aims of which are described on the main iTEM website.

.. contents::
   :local:

Sources
=======
These are listed in :file:`sources.yaml` from the `iTEM metadata repository <https://github.com/transportenergy/metadata>`_.
The current version of the file is always accessible at https://github.com/transportenergy/metadata/blob/master/historical/sources.yaml

Input data is retrieved using via OpenKAPSARC and SDMX APIs, according to the type supported by each data source. See :mod:`item.remote`.

Processing
==========

Input data sets are cleaned and transformed by IPython notebooks in the :file:`item/historical/scripts` directory.

In general, the notebook name corresponds to the input data set which it handles.

Diagnostics
===========

:mod:`.diagnostic` contains two kinds of **diagnostics**, which are descriptions of part or all of a data set:

- **coverage** concerns which areas (countries or regions), time periods, and measures are included, or not.
- **quality** includes sanity checks, such as computed/derived statistics for data, and their comparison to reference values.

Automated diagnostics
---------------------

These can be run using the CLI command ``ixmp historical diagnostic FOLDER``.
Output is produced in a new folder named :file:`FOLDER`.

On our continuous integration infrastructure, for every build, these diagnostics are run automatically and uploaded to cloud storage for reference.
For instance:

- For `GitHub pull request #23 <https://github.com/transportenergy/database/pull/23>`_, the Travis CI service produced `build number 313 <https://travis-ci.com/github/transportenergy/database/builds/156068167>`_.
- The uploaded diagnostics from this build are available at: https://storage.googleapis.com/historical-data-ci.transportenergy.org/313.1/index.html


Code reference
==============

.. automodule:: item.historical
   :members:
   :exclude-members: REGION, SOURCES

   .. Omit the verbose printing of the data values.

   .. autodata:: item.historical.REGION
      :annotation:

   .. autodata:: item.historical.SOURCES
      :annotation: ← contents of sources.yaml
