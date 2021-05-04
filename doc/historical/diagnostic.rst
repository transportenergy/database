Diagnostics
***********

:mod:`.historical.diagnostic` contains two kinds of **diagnostics**, which are descriptions of part or all of a data set:

- **coverage** concerns which areas (countries or regions), time periods, and measures are included, or not.
- **quality** includes sanity checks, such as computed/derived statistics for data, and their comparison to reference values.

Automated diagnostics
=====================

These can be run using the CLI command ``ixmp historical diagnostic FOLDER``.
Output is produced in a new folder named :file:`FOLDER`.

.. currentmodule:: item.historical.diagnostic

.. automodule:: item.historical.diagnostic
   :members:


Specific diagnostic tests
=========================

A001
----

.. currentmodule:: item.historical.diagnostic.A001

.. automodule:: item.historical.diagnostic.A001
   :members:

A002
----

.. currentmodule:: item.historical.diagnostic.A002

.. automodule:: item.historical.diagnostic.A002
   :members:

A003
----

.. currentmodule:: item.historical.diagnostic.A003

.. automodule:: item.historical.diagnostic.A003
   :members:
