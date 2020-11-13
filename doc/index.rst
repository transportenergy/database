International Transport Energy Modeling (iTEM) toolkit
******************************************************

`iTEM`_ maintains two databases:

1. A **model database** of transport energy projections assembled as part of
   the `iTEM workshops`_, of which there have been four so far, with a fifth
   planned for early 2020.

2. A **historical database** to form a common, public, “best available”
   baseline for model calibration and projections.

This documentation, built automatically from the `transportenergy/database GitHub repository <https://github.com/transportenergy/database>`_, describes the Python and R toolkit for maintaining these databases.

.. _iTEM: http://transportenergy.org
.. _iTEM workshops: http://transportenergy.org/workshops
.. _iTEM organizing group:
   http://transportenergy.org/participants#organizing-group

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   model
   historical
   structure
   remote
   cli
   metadata
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

Copyright © 2017–2020 iTEM contributors

The software is licensed under the `GNU General Public License, version 3 <http://www.gnu.org/licenses/gpl-3.0.en.html>`_.

.. _citation:

If you use or reference data from either iTEM database, or use the code, in preparation of any scientific publication, please :ref:`cite the appropriate reference <usage-cite>`.
