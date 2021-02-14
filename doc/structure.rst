Data structures
***************

iTEM defines :doc:`metadata <metadata>` using the SDMX information model, in order to specify the contents and various formats/representations of both the :doc:`historical <historical>` and :doc:`model projection <model>` data flows and data sets.

Overview
========

This section briefly summarizes the contents of the iTEM :ref:`structure-xml`.
It does not give a complete or exhaustive terminology for SDMX; see the :doc:`sdmx:resources` page in the :mod:`sdmx` documentation for further reading.

It is common to call certain things “columns”; this creates problems because it conflates the *logical structure* of data with a *particular representation*, e.g. in a table.
By describing the structure itself, we allow for multiple representations that are suitable for different purposes, yet easily interoperable.

General
   All the data structures have a uniform resource name (URN) like: ``urn:sdmx:org.sdmx.infomodel.datastructure.DataStructureDefinition=iTEM:HISTORICAL(0.1)``.
   This identifies:

   - what kind of object it is (here, a data structure definition, or DSD).
   - who the reponsible Organization or Agency is (iTEM).
   - the ID of the thing (``HISTORICAL`` DSD), and
   - a version number (0.1).

   Specific data need not copy the entire DSD, merely refer to it using the URN.
   The DSD can be updated over time, incrementing the version, while references to older versions remain valid.

Concept scheme ``TRANSPORT``
   This scheme includes concepts that are commonly used as dimensions or attributes for transport data.
   These are typically represented by a set of discrete codes.

   Each Concept is an SDMX ‘Item’ and so it has an *id* (usually in upper case), and optionally a *name* and *description* (both can be multi-lingual), and zero or more annotations.

Concept scheme ``TRANSPORT_MEASURES``
   This scheme includes concepts that are *measures*, i.e. the thing that is measured by the quantity (magnitude and unit) of a particular observation.

Code lists
   :file:`structure.xml` includes lists of codes used to represent particular concepts.
   For instance, ``CL_LCA_SCOPE`` gives three Codes with the ids “TTW”, “WTT”, and “WTW”.
   (As Items, Codes can also have plain-language names and longer descriptions. The ID is used for a short, machine readable representation.)

   A statement like “this data set has a dimension ``LCA_SCOPE`` that represents the concept ``LCA_SCOPE`` using the code list ``CL_LCA_SCOPE``” is clear and unambiguous about the structure of that particular data set.
   A econd data set can be described as having “an *attribute* ``LCA_SCOPE`` that represents the concept ``LCA_SCOPE`` using the code list ``CL_LCA_SCOPE``”; this is a distinct structure and representation, but completely interoperable with the first.


Code reference
==============

.. currentmodule:: item.sdmx

.. automodule:: item.sdmx
   :members:

.. currentmodule:: item.structure

.. autofunction:: make_template

.. automodule:: item.structure
   :members:
   :exclude-members: make_template, read_items, read_concepts_yaml, read_measures_yaml

   The following utility functions are used by :func:`make_template`:

   .. autosummary::

      add_unit
      collapse
      common_dim_dummies
