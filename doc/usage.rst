Usage
*****

The following instructions are not language-specific.
Both the Python and R tools will operate on data stored in the following way; see the language-specific sections below for more details.

1. Install the Python package, or clone the repository and install the code in both languages.

2. Create 1 or more separate directory to contain the input and output files.
   A simple way to do this is to call ``$ item mkdirs PATH``, where ``PATH`` is a base directory; this will create a tree of directories.
   Use ``item mkdirs --help`` for more information.

3. Copy the file ``item_config_example.yaml`` to ``item_config.yaml`` in any working directory where you intend to use this code.
   Edit the file (see the inline comments) to point to the directories created in #2 above.

4. Use the tools through the :doc:`cli`.


Installation
============

Use `pip <https://pip.pypa.io/en/stable/>`_.
From `PyPI <https://pypi.org/project/transport-energy/>`_::

    $ pip install transport-energy

From source (for instance, to develop the code locally)::

    $ git clone --recurse-submodules git@github.com:transportenergy/database.git
    $ cd database
    $ pip install --editable .[doc,hist,tests]

Or, without cloning the repository::

    $ pip install --editable git://github.com/transportenergy/database#egg=item@subdirectory=python [doc,hist,tests]


Usage
=====

From Python scripts, import the :mod:`item` module or submodules and call specific functions described elsewhere in this documentation.
For instance::

    from item import historical, model, structure

    # Display information about the cleaning script for
    # one historical data set
    help(historical.T009)

    # Generate a template for model data
    structure.make_template()

    # Display metadata (information about a model's data)
    model.load_model_regions("itf", version=2)


Run tests
=========

Unit and integration tests in :mod:`item.tests` can be run with `pytest <https://pytest.org/>`_.
The command-line option ``--local-data`` can be used to point to local data files, e.g. the model database, not included in the Git repository::

    $ py.test --local-data=../../data/model/database item
    ================ test session starts ================
    …


.. _usage-cite:

Cite the data or code
=====================

If you use or reference data from either iTEM database, or use the code, in preparation of any scientific publication, please cite the appropriate reference.

- Automatically-generated DOIs via Zenodo, either:

  - `10.5281/zenodo.4271788 <https://doi.org/10.5281/zenodo.4271788>`_, which represents *all versions* of the software, and always resolves to the latest version, or
  - the DOI for a *specific version*. For instance, `10.5281/zenodo.4271789 <https://doi.org/10.5281/zenodo.4271789>`_ is the DOI for :mod:`item` version 2020.11.13.

- DOI `10.5281/zenodo.4121180 <https://doi.org/10.5281/zenodo.4121180>`_ for the 2020-04-15 version of the historical database, which includes a snapshot of the data and a PDF document describing some of the data cleaning steps.

The Zenodo pages provide downloadable citations in BibTeX and many other formats, for use in the reference management software of your choice.
