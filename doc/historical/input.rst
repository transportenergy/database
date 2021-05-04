Input data
**********

Every input data set has a corresponding Python module to adjust the unprocessed data provided directly by the upstream data source to the common iTEM structure.

These modules are not invoked directly, but through the function :func:`~historical.process`, e.g.

.. code-block:: python

   # Process upstream data for data set T009; return the results
   process(9)

:func:`~historical.process` loads and makes use of *dataset-specific* configuration, checks, and additional code from the corresponding submodule,
while automating common cleaning steps.
See:

- the function documentation for a complete description of these steps.
- the green [source] link next to each function (e.g. :func:`.T001.process`) to access and inspect the source code for the dataset-specific cleaning steps.

This pattern reduces duplicated code in each dataset-specific submodule, while remaining flexible to upstream data formats.

.. _howto-input-data:

HOWTO add upstream data sources or sets
=======================================

- Add the data set entry to :file:`sources.yaml`.
- Copy, rename, and modify an existing module, e.g. :file:`T012.py`.
- Extend the tests to ensure this data set is tested.
- Update the docstrings in the code and this documentation.

Common code
===========

.. currentmodule:: item.historical

.. automodule:: item.historical
   :members:
   :exclude-members: REGION, SOURCES

.. autodata:: item.historical.REGION
   :annotation:

.. autodata:: item.historical.SOURCES
   :annotation: ← contents of sources.yaml


T000
====

.. currentmodule:: item.historical.T000

.. automodule:: item.historical.T000
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 1-9

T001
====

.. currentmodule:: item.historical.T001

.. automodule:: item.historical.T001
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 11-18

T002
====

.. currentmodule:: item.historical.T002

.. automodule:: item.historical.T002
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 20-27

T003
====

.. currentmodule:: item.historical.T003

.. automodule:: item.historical.T003
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 29-36

T004
====

.. currentmodule:: item.historical.T004

.. automodule:: item.historical.T004
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 38-40

T005
====

.. currentmodule:: item.historical.T005

.. automodule:: item.historical.T005
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 42-47

T006
====

.. currentmodule:: item.historical.T006

.. automodule:: item.historical.T006
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 49-54

T007
====

.. currentmodule:: item.historical.T007

.. automodule:: item.historical.T007
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 56-61

T008
====

.. currentmodule:: item.historical.T008

.. automodule:: item.historical.T008
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 63-68

T009
====

.. currentmodule:: item.historical.T009

.. automodule:: item.historical.T009
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 70-75

T010
====

.. currentmodule:: item.historical.T010

.. automodule:: item.historical.T010
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 77-82

T012
====

.. currentmodule:: item.historical.T012

.. automodule:: item.historical.T012
   :members:

.. literalinclude:: ../../item/data/historical/sources.yaml
   :language: yaml
   :lines: 91-96
