Development notes
*****************

Repository organization
=======================

- ``item/`` — Python code for accessing & maintaining the database.

  - ``data/`` — *Meta* -data about the iTEM databases. Actual data is stored separately; see below.

    - ``model/`` — Metadata about the iTEM model database. Many of these files are in `YAML format <http://www.yaml.org/spec/1.2/spec.html>`_ (`Wikipedia <https://en.wikipedia.org/wiki/YAML>`_), with more detailed comments in-line.

      - ``models.yaml`` — description of the `iTEM participating models & teams <https://transportenergy.org/participants/>`_.
      - ``dimensions/`` — information about the `data dimensions of the model database <https://transportenergy.org/database/>`_.
      - Other directories:

        - are named to match the keys in ``models.yaml``,
        - contain model-specific metadata, including but not limited to:

          - ``regions.yaml``: regional aggregation.
          - ``scenarios.yaml``: descriptions of scenarios submitted to each iTEM workshop.
    - ``concepts.yaml``, ``measures.yaml``, ``spec.yaml`` — specifications of data to be submitted for for the 3rd iTEM MIP.
    - ``item_config_example.yaml`` — an example configuration file.


.. _code-style:

Code style
==========

- Run the following tools on all new and modified code::

      isort . && black . && mypy . && flake8

  The continuous integration workflow checks that these have been applied; PRs will fail unless they are.

- Document all public classes and functions following the `NumPy docstring
  format`_.
- Ensure new items appear in the built documentation.
- All code must be importable from within :mod:`item`.
- Clear all cell output, execution counts, etc. from IPython notebooks committed to the repository.

.. _Numpy docstring format: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard


Preparing a new release
=======================

Before releasing, check:

- https://github.com/transportenergy/database/actions?query=workflow:pytest+branch:main to ensure that the push and scheduled builds are passing.
- https://readthedocs.org/projects/transportenergy/builds/ to ensure that the docs build is passing.

Address any failures before releasing.

1. Edit :file:`doc/whatsnew.rst`.
   Comment the heading "Next release", then insert another heading below it, at the same level, with the version number and date.
   Make a commit with a message like "Mark vX.Y.Z in doc/whatsnew".

2. Tag the release candidate version, i.e. with a ``rcN`` suffix, and push::

    $ git tag v2021.5.4rc1
    $ git push --tags origin main

   :mod:`item` uses a versioning scheme of **[year].[month].[day]**.
   For instance, the version released on October 4, 2030 will have the version ``2030.10.4``.
   Note that:

   - There are no leading zeroes.
   - If two versions are to be released in a single day—for instance, to fix a bug only spotted after release—a fourth version part can be added, e.g. ``2030.10.4.1``.

3. Check:

   - at https://github.com/transportenergy/database/actions?query=workflow:publish that the workflow completes: the package builds successfully and is published to TestPyPI.
   - at https://test.pypi.org/project/transport-energy/ that:

      - The package can be downloaded, installed and run.
      - The README is rendered correctly.

   Address any warnings or errors that appear.
   If needed, make a new commit and go back to step (2), incrementing the rc number.

4. (optional) Tag the release itself and push::

    $ git tag v2021.5.4
    $ git push --tags origin main

   This step (but *not* step (2)) can also be performed directly on GitHub; see (5), next.

5. Visit https://github.com/transportenergy/database/releases and mark the new release: either using the pushed tag from (4), or by creating the tag and release simultaneously.

6. Check at https://github.com/transportenergy/database/actions?query=workflow:publish and https://pypi.org/project/transport-energy/ that the distributions are published.
