Historical & statistical data (:mod:`item.historical`)
******************************************************

This module contains the code that implements the `iTEM Open Data project <https://transportenergy.org/open-data/>`_, the broader aims of which are described on the main iTEM website.

See also the :doc:`glossary`, which gives precise terminology used on this page.

.. contents::
   :local:

Sources
=======
These are listed in :file:`sources.yaml`, loaded as :data:`.SOURCES`, from the `iTEM metadata repository <https://github.com/transportenergy/metadata>`_.

Input data is retrieved using via OpenKAPSARC and SDMX APIs, according to the type supported by each data source. See :mod:`item.remote`.


Processing
==========

The general function :func:`~historical.process` applies common cleaning steps to each dataset, while loading and making use of dataset-specific checks, processing steps, and configuration from a submodule like :mod:`.T001`.
See the documentation of :func:`~historical.process` for a detailed description of the steps.

.. _diagnostics:

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

.. currentmodule:: item.historical

.. automodule:: item.historical
   :members:
   :exclude-members: REGION, SOURCES

   .. Omit the verbose printing of the data values.

   .. autodata:: item.historical.REGION
      :annotation:

   .. autodata:: item.historical.SOURCES
      :annotation: ← contents of sources.yaml

.. currentmodule:: item.historical.diagnostic

.. automodule:: item.historical.diagnostic
   :members:

Specific data sets
==================

T000
----

.. currentmodule:: item.historical.T000

.. automodule:: item.historical.T000
   :members:

   .. literalinclude:: ../item/data/historical/sources.yaml
      :language: yaml
      :lines: 1-10


T001
----

.. currentmodule:: item.historical.T001

.. automodule:: item.historical.T001
   :members:

   .. literalinclude:: ../item/data/historical/sources.yaml
      :language: yaml
      :lines: 12-20


T003
----

.. currentmodule:: item.historical.T003

.. automodule:: item.historical.T003
   :members:

   .. literalinclude:: ../item/data/historical/sources.yaml
      :language: yaml
      :lines: 32-40

T004
----

.. currentmodule:: item.historical.T004

.. automodule:: item.historical.T004
   :members:

   .. literalinclude:: ../item/data/historical/sources.yaml
      :language: yaml
      :lines: 42-45

T009
----

.. currentmodule:: item.historical.T009

.. automodule:: item.historical.T009
   :members:

   .. literalinclude:: ../item/data/historical/sources.yaml
      :language: yaml
      :lines: 75-80

T010
----

.. currentmodule:: item.historical.T010

.. automodule:: item.historical.T010
   :members:

T012
----

.. currentmodule:: item.historical.T012

.. automodule:: item.historical.T012
   :members:


Quality diagnostics
===================

A003
----

.. currentmodule:: item.historical.diagnostic.A003

.. automodule:: item.historical.diagnostic.A003
   :members:
