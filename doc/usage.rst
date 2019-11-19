Usage
*****

The following instructions are not language-specific.
Both the Python and R tools will operate on data stored in the following way; see the language-specific sections below for more details.

1. Clone the repository and/or install the code in one or both languages.

2. Create 1 or more separate directory to contain the input and output files.
   A simple way to do this is to call ``$ item mkdirs PATH``, where ``PATH`` is a base directory; this will create a tree of directories.
   Use ``item mkdirs --help`` for more information.

3. Copy the file ``item_config_example.yaml`` to ``item_config.yaml`` in any working directory where you intend to use this code.
   Edit the file (see the inline comments) to point to the directories created in #2 above.

4. Use the tools through the command-line interface::

    $ item
    Usage: item [OPTIONS] COMMAND [ARGS]...

      Command-line interface for the iTEM databases.

    Options:
      --path <KEY> <PATH>  Override data paths (multiple allowed).
      --help               Show this message and exit.

    Commands:
      debug     Show debugging information, including paths.
      help      Show extended help for the command-line tool.
      mkdirs    Create a directory tree for the database.
      model     Manipulate the model database.
      stats     Manipulate the stats database.
      template  Generate the MIP3 submission template.


Installation
============
Use `pip <https://pip.pypa.io/en/stable/>`_.
From source (for instance, to develop the code locally)::

    $ git clone --recurse-submodules git@github.com:transportenergy/database.git
    $ cd database
    $ pip install --editable .[doc,hist,tests]

Or, without cloning the repository::

    $ pip install --editable git://github.com/transportenergy/database#egg=item@subdirectory=python


Usage
=====

From Python scripts::

    import item

    data = item.load_model_data(1)


Run tests
=========

Tests in ``item/tests`` can be run with `py.test <https://pytest.org/>`_.
The command-line option ``--local-data`` must be defined in order for these tests to work::

    $ py.test --local-data=../../data/model/database item
    ================ test session starts ================
    …
