Overview
********

This module (:mod:`item.historical`) contains the code that implements the `iTEM Open Data project <https://transportenergy.org/open-data/>`_, the broader aims of which are described on the main iTEM website.

See also the :doc:`glossary`, which gives precise terminology used on this page.

.. digraph:: historical_1
   :caption: High-level flow of historical data

   rankdir = "LR"

   {
     Upstream [shape=rect]
     fetch [shape=cds]
     process [shape=cds]
     assemble [shape=cds]
     Cache [shape=rect]
     upload [shape=cds]
     Cloud [shape=rect]
     publish [shape=cds]
     final [shape=rect label="Published data"]
   }

   Upstream -> fetch -> process -> assemble -> Cache -> upload -> Cloud -> publish -> final;
   fetch -> Cache;
   process -> Cache;

In this diagram, rectangles indicate data “at rest”, and right-arrows indicate *operations* on data.
These steps are described below:

Fetch
  In order to enable :doc:`/repro`, the data **may be** fetched, or retrieved, from their original online sources *every time the code runs*.
  This contributes to quality in multiple ways:

  - Additions to the input data (e.g. for newer time periods, or infill of data gaps) are automatically and quickly incorporated.
  - Changes to the input data are detected, and can be addressed if they impact quality.

  Input data is retrieved using code in :mod:`item.remote`, including via SDMX, OpenKAPSARC, and other APIs, according to the source.
  These are listed in :file:`sources.yaml`, loaded as :data:`.SOURCES`, from the `iTEM metadata repository <https://github.com/transportenergy/metadata>`_.

  These sources are often not “raw” or primary sources; they can be organizations (e.g. NGOs) that themselves collect, aggregate, and/or harmonize data from sources *further* upstream (e.g. national statistical bodies).
  iTEM thus avoids the need to duplicate the work done by sources.

Cache
  Data is *cached*, or stored in local files, at *multiple points* along the data ‘pipeline’.
  This enables:

  - Debugging,
  - Direct use of the intermediate data, if desired,
  - Performance improvement. For instance, if the same upstream data is requested twice in the same program, it is only fetched over the Internet once; the second time, it is read from cache.

Process (‘clean’)
  For each upstream data source, there is a simple Python module that cleans the data and aligns it to the the iTEM data structure.
  See :doc:`input` for a description of these modules.


Assemble
  The input data, now cleaned and converted to a common structure, are combined into a single data set.

  This stage can include additional steps, such as:

  - Compute derived quantities.
  - Merge and infill; resolve duplicates (same data key from 2 or more sources).
  - Harmonization and adjustment.
  - Perform :doc:`diagnostic`.

Upload to cloud
  The entire cache—unprocessed upstream/input data; processed/cleaned data; and assembled data—are uploaded to Google Cloud Storage

  On our continuous integration infrastructure, this occurs for every build, at every commit of the code.
  For instance:

  - For GitHub :pull:`71`, the GitHub Actions build produced `build number 41 <https://github.com/transportenergy/database/runs/2476980208>`_.
  - The uploaded diagnostics from this build are available at: https://storage.googleapis.com/data.transportenergy.org/historical/ci/41/index.html

Publish
  Periodically, the iTEM team will manually publish an update of the “official” database.
  This includes:

  1. Take the latest automatically generated/uploaded cache.
  2. Inspect it for further issues.
  3. Mark the code version used to produce it with a version number.
  4. Publish the assembled data set on Zenodo, with reference to the code version.
