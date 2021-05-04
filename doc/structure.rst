Data structures
***************

iTEM defines :doc:`metadata <metadata>` using the SDMX information model, in order to specify the contents and various formats/representations of both the :doc:`historical <historical/overview>` and :doc:`model projection <model>` data flows and data sets.

Overview
========

This section briefly summarizes the contents of the iTEM :ref:`structure-xml`.
It does not give a complete or exhaustive terminology for SDMX; see the :doc:`sdmx:resources` page in the :mod:`sdmx` documentation for further reading.

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

Concept scheme ``MODELING``
   This scheme includes concepts related to model-based research, including ``MODEL``, ``SCENARIO`` ,etc.

Code lists
   :file:`structure.xml` includes lists of codes used to represent particular concepts.
   For instance, ``CL_LCA_SCOPE`` gives three Codes with the ids “TTW”, “WTT”, and “WTW”.
   (As Items, Codes can also have plain-language names and longer descriptions. The ID is used for a short, machine readable representation.)

   A statement like “this data set has a dimension ``LCA_SCOPE`` that represents the concept ``LCA_SCOPE`` using the code list ``CL_LCA_SCOPE``” is clear and unambiguous about the structure of that particular data set.
   A second data set can be described as having “an *attribute* ``LCA_SCOPE`` that represents the concept ``LCA_SCOPE`` using the code list ``CL_LCA_SCOPE``”; this is a distinct structure and representation, but completely interoperable with the first.

   Some **standard IDs** are used in multiple code lists, mirroring other applications of SDMX.
   These include:

   - ``_Z``: “Not applicable”, when it does not make logical sense to give a value on this concept/dimension for this data.
   - ``_T``: “Total”, the sum of all data.
     This is sometimes called “All”.
   - ``_X``: “Not allocated/unknown”, data not associated to any other code in the list.


To obtain and use data structure information in code that works with iTEM data, use :func:`generate`.
For example:

.. code-block:: python

    >>> from item.structure import generate

    # Generate an SDMX "structure message" containing all the data structures
    >>> sm = generate()

    # Select the historical data structure definition
    >>> sm.structure["HISTORICAL"]
    <DataStructureDefinition iTEM:HISTORICAL(0.1)>

    # Show the dimensions of the data structure
    >>> dsd = sm.structure["HISTORICAL"]
    >>> dsd.dimensions
    <DimensionDescriptor: <Dimension SERVICE>; <Dimension MODE>; <Dimension VEHICLE>; <Dimension FUEL>; <Dimension TECHNOLOGY>; <Dimension AUTOMATION>; <Dimension OPERATOR>; <Dimension POLLUTANT>; <Dimension LCA_SCOPE>; <Dimension FLEET>; <MeasureDimension VARIABLE>>

    # Get one dimension
    >>> dim = dsd.dimensions.get("LCA_SCOPE")
    >>> dim
    <Dimension LCA_SCOPE>

    # Navigate from the dimension to the list of codes used to represent it
    >>> dim.local_representation.enumerated
    <Codelist iTEM:CL_LCA_SCOPE(0.1) (4 items)>

    # Show the codes in this code list
    >>> codelist = dim.local_representation.enumerated
    >>> codelist.items
    {'_Z': <Code _Z: Not applicable>,
     'TTW': <Code TTW: Tank-to-wheels>,
     'WTT': <Code WTT: Well-to-tank>,
     'WTW': <Code WTW: Well-to-wheels>}

    # Show the valid concepts to appear in the VARIABLE dimension
    >>> dsd.dimensions.get("VARIABLE").local_representation.enumerated.items
    {'ACTIVITY': <Concept ACTIVITY: Transport activity>,
     'ENERGY': <Concept ENERGY: Energy>,
     'ENERGY_INTENSITY': <Concept ENERGY_INTENSITY: Energy intensity of activity>,
     'EMISSION': <Concept EMISSION: Emission>,
     'GDP': <Concept GDP: Gross Domestic Product>,
     'LOAD_FACTOR': <Concept LOAD_FACTOR: Load factor>,
     'POPULATION': <Concept POPULATION: Population>,
     'PRICE': <Concept PRICE: Price>,
     'SALES': <Concept SALES: Sales>,
     'STOCK': <Concept STOCK: Stock>}


Code reference
==============

.. currentmodule:: item.structure

.. automodule:: item.structure
   :members:

.. currentmodule:: item.structure.base

.. automodule:: item.structure.base
   :members:

.. currentmodule:: item.structure.sdmx

.. automodule:: item.structure.sdmx
   :members:

.. automodule:: item.structure.template
   :members:

   The following utility functions are used by :func:`make_template`:

   .. autosummary::

      add_unit
      collapse
      name_for_id
