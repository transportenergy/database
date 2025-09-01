:tocdepth: 2

What's new?
***********

Next release
============

- Drop submodule/packaging of transportenergy/metadata (:pull:`99`);
  instead, fetch these files over the network and cache them.
- New class :class:`.ModelInfo` (:pull:`99`),
  replacing an old/unspecified YAML syntax for information about participating models.
  Instances of this class are in submodules of :mod:`item.model`,
  including 5 new submodules.
- New :func:`.structure.sdmx.make_iamc_variable_cl` (:pull:`99`).
- New :func:`.util.metadata_repo_file` (:pull:`99`).

v2025.3.31
==========

- Bug fix: the v2025.3.30 release omitted some package data files, leading to issues like :issue:`96` (:pull:`97`).

v2025.3.30
==========

- Add :mod:`.A001` and :mod:`.A002` historical quality diagnostics (:pull:`74`).
- Adjust for compatibility with `NumPy 2 <https://numpy.org/doc/stable/release/2.0.0-notes.html>`_ (:pull:`87`).
- Drop support for Python version 3.8, which has reached EOL; test and declare support for Python 3.13 (:pull:`93`).

v2021.5.4
=========

- Add data cleaning for the :mod:`.T005`, :mod:`.T006`, :mod:`.T007`, :mod:`.T008` historical input data sources (:pull:`71`).
- Add data cleaning for the :mod:`.T004` historical input data source (:pull:`59`).
- Update :doc:`usage` documentation (:issue:`41`, :pull:`43`).
- Increase minimum Python version to 3.7 and ensure compatibility (:issue:`41`, :pull:`43`).
- Add the :doc:`glossary` page (:pull:`42`).
- Correct an error in the input data for :mod:`.T001` (:issue:`32`, :pull:`40`).

v2020.11.13
===========

- Initial release on PyPI.
