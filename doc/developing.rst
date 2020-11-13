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


Style guide
===========

- Run the following tools on all new and modified code::

      isort -rc . && black . && mypy . && flake8

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

- https://github.com/transportenergy/actions?query=workflow:pytest+branch:master to ensure that the push and scheduled builds are passing.
- https://readthedocs.org/projects/transportenergy/builds/ to ensure that the docs build
  is passing.

Address any failures before releasing.


1. Edit :file:`doc/whatsnew.rst` to replace "Next release" with the version number and date.
   Make a commit with a message like "Mark vX.Y.Z in whatsnew.rst".

2. Tag the version, e.g.::

    $ git tag v2030.10.4b4

   :mod:`item` uses a versioning scheme of **[year].[month].[day]**.
   For instance, the version released on October 4, 2030 will have the version ``2030.10.4``.
   Note that:

   - There are no leading zeroes.
   - If two versions are to be released in a single day—for instance, to fix a bug only spotted after release—a fourth version part can be added, e.g. ``2030.10.4.1``.

3. Test-build and check the source and binary packages::

    $ rm -rf build dist
    $ python setup.py bdist_wheel sdist
    $ twine check dist/*

   Address any warnings or errors that appear.
   If needed, make a new commit and go back to step (2).

4. Upload the packages to the TEST instance of PyPI::

    $ twine upload -r testpypi dist/*

5. Check at https://test.pypi.org/project/transport-energy/ that:

   - The package can be downloaded, installed and run.
   - The README is rendered correctly.
   - Links to the documentation go to the correct version.

   If not, modify the code and go back to step (2).

6. Upload to PyPI::

    $ twine upload dist/*

7. Push the commit(s) and tag to GitHub::

    $ git push --tags

8. Edit :file:`doc/whatsnew.rst` to add a new heading for the next release.
