.. iTEM documentation master file, created by
   sphinx-quickstart on Thu Dec 13 16:24:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

International Transport Energy Modeling (iTEM) toolkit
======================================================

`iTEM`_ maintains two databases:

1. A **model database** of transport energy projections assembled as part of
   the `iTEM workshops`_, of which there have been four so far, with a fifth
   planned for early 2020. Because of restrictions from workshop participants,
   the model database is currently *not public*, but only available to iTEM
   workshop participants.

2. A **historical database** to form a common, public, “best available”
   baseline for model calibration and projections. The statistics database is
   currently *under development*.

This repository contains tools for *both* databases, in *both* Python and R. The goals for these tools are that:

- iTEM participants use the tools to *access* either database and perform basic
  data manipulations such as retrieval, selection, and aggregation, in either
  Python, R (or possibly, in the future, other languages).
- Members of the `iTEM organizing group`_ use the tools to prepare templates
  for data submission, and to aggregate & clean submitted data.
- iTEM participants, if they choose, maintain code that *transparently &
  reproducibly* derives the iTEM variables from immediate output files of their
  models.
- The tools are well-tested and yield reproducible results.

.. _iTEM: http://transportenergy.org
.. _iTEM workshops: http://transportenergy.org/workshops
.. _iTEM organizing group:
   http://transportenergy.org/participants#organizing-group


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   model
   historical
   reference


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
