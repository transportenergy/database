Reproducibility
***************

In software development, the term “continuous integration” (CI) refers to a process to check that pieces of code can be ‘integrated’, e.g. built and run together, and that they perform as expected.
The process is ‘continuous’ because it is automatically performed for incremental changes in the code, e.g. Git commits.
CI enables efficient use of resources (in particular, people's time) by reducing or eliminating manual work in performing these checks.

This page details how iTEM uses CI practices to enable **continuous reproduction and validation**, i.e. to reduce manual work in checking the validity of methods, data, and results related to transport data.

GitHub Actions
==============

Every pull request to the ``transportenergy/database`` has the following checks run on it.
The different checks, or *jobs*, are described by *workflow files*:

- :file:`.github/workflows/cq.yaml`
- :file:`.github/workflows/pytest.yaml`

These files are interpreted by `GitHub Actions <https://docs.github.com/en/actions>`_ to set up and control the jobs (follow the link for extensive documentation).

Test suite & diagnostics
------------------------

pytest
   This runs the test suite, which is in the files under :file:`item/tests/`.
   These are implemented using `pytest <https://docs.pytest.org>`_.

   The *coverage*—details of which statements of the code are executed at least once during the tests, and which are missing—is uploaded to Codecov.

Upload historical database and diagnostics
   The :ref:`cli` command ``item historical diagnostics`` is run to completely regenerate the historical database and diagnostic calculations based on it.
   The results are uploaded to Google Cloud Storage, and a link to the :file:`index.html` is published to the pull request on GitHub.

   The file contains the following sections:

   Coverage
      One file for each input data set that summarizes the data included in the input data.

   Quality
      The outputs of other :doc:`diagnostic <historical/diagnostic>` checks of intermediate or output data.

   Input data
      A copy of the input data retrieved from each upstream data source at the time of the build.

Code quality
------------

black, flake8, mypy
   Check that the :ref:`code-style` has been properly applied.

Sphinx docs
   Check that the documentation in :file:`doc/` can be built without errors.
   The documentation on https://transportenergy.rtfd.io is built separately and hosted by `Read The Docs <https://readthedocs.org>`_.
   This check is only to flag potential issues in the build.

twine
   Check that the Python package can be built.
