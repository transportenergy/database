Metadata
********

Metadata (i.e. data that describe iTEM data) are stored in the public `transportenergy/metadata <https://github.com/transportenergy/metadata>`_ repository.
This page displays some of these metadata files.

To make use of these files:

- Install :mod:`item` and use its methods to retrieve the files in useful Python data formats.
- Include this repository as a `git submodule <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`_—as is done in the transportenergy/database repo used to build the :mod:`item` package and this documentation.

.. contents::
   :local:


.. _concepts-yaml:

Concept schemes (:file:`concepts.yaml`)
=======================================

iTEM uses the :mod:`sdmx` notion of a "concept scheme": a (possibly) hierarchical list of distinct concepts.
Per the :ref:`SDMX 'information model' <sdmx:im-base-classes>`, each of these :class:`.Concepts` has an `id` and optionally a `name`, a `description`, and one or more annotations.

The concepts in :file:`concepts.yaml` are all measured using *discrete, unordered codes*: for instance, the 'lca_scope' of a particular data observation might be 'ttw', 'wtt', or one of the other values.

In contrast, the :ref:`measures <measures-yaml>` below are measured in *continuous, quantiative* values.

.. literalinclude:: ../item/data/concepts.yaml
   :language: yaml


.. _measures-yaml:

Measures (:file:`measures.yaml`)
================================

'measure' is another :ref:`Concept Scheme <concepts-yaml>`.
Each measure also has an annotation specifying `units`; see :func:`add_unit`.

.. literalinclude:: ../item/data/measures.yaml
   :language: yaml


.. _spec-yaml:

iTEM template specification (:file:`spec.yaml`)
===============================================

.. literalinclude:: ../item/data/spec.yaml
   :language: yaml
