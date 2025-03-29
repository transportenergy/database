International Transport Energy Modeling (iTEM) toolkit
******************************************************

`iTEM`_ maintains two databases:

1. A **historical database** to form a common, public, “best available” baseline for model calibration and projections.
   The historical database is under continuous development.

2. A **model database** of transport energy projections assembled as part of the iTEM model intercomparison projects (MIPs) linked to `iTEM workshops`_.
   To meet the intellectual property concerns of workshop participants, the model database is currently not public, and only available on request; however, the tools used to prepare it are public.
   These tools are developed periodically, during sequential MIPs.

This documentation, built automatically from the `transportenergy/database GitHub repository <https://github.com/transportenergy/database>`_, describes the Python and R code for maintaining these databases.

.. _iTEM: http://transportenergy.org
.. _iTEM workshops: http://transportenergy.org/workshops
.. _iTEM organizing group:
   http://transportenergy.org/participants#organizing-group

.. toctree::
   :maxdepth: 2
   :caption: General

   usage
   structure
   repro
   glossary

.. toctree::
   :maxdepth: 2
   :caption: Historical data

   historical/overview
   historical/input
   historical/diagnostic

.. toctree::
   :maxdepth: 2
   :caption: Model data

   model

.. toctree::
   :maxdepth: 2
   :caption: Package info

   metadata
   remote
   whatsnew
   developing


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Goals
=====

The goals for these tools are that:

- iTEM participants use the tools to *access* either database and perform basic
  data manipulations such as retrieval, selection, and aggregation, in either
  Python, R (or possibly, in the future, other languages).
- Members of the `iTEM organizing group`_ use the tools to prepare templates
  for data submission, and to aggregate & clean submitted data.
- iTEM participants, if they choose, maintain code that *transparently &
  reproducibly* derives the iTEM variables from immediate output files of their
  models.
- The tools are well-tested and yield reproducible results.
- The tools are fully documented.

License
=======

Copyright © 2017–2025 iTEM contributors

The software is licensed under the `GNU General Public License, version 3 <http://www.gnu.org/licenses/gpl-3.0.en.html>`_.

.. _citation:

If you use or reference data from either iTEM database, or use the code, in preparation of any scientific publication, please :ref:`cite the appropriate reference <usage-cite>`.
