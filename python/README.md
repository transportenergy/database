Python tools for the iTEM databases
===================================

Installation
------------
Use [`pip`](https://pip.pypa.io/en/stable/). From source (for instance, to develop the code locally):

```
$ git clone git@github.com:transportenergy/database.git
$ pip install -e database/python
```

Or without cloning the repository:

```
$ pip install -e git://github.com/transportenergy/database#egg=item@subdirectory=python
```

Usage
-----

### From Python scripts

```python
import item

data = item.load_model_data(1)
```

### Command line

`run` is an executable that provides access to some package functions.

```
$ ./run
Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

  Command-line interface for the iTEM databases.

…

Options:
  --path <KEY> <PATH>  Override data paths (multiple allowed).
  --help               Show this message and exit.

Commands:
  debug   Show debugging information, including paths.
  mkdirs  Create a directory tree for the database.
  model   Manipulate the model database.
  stats   Manipulate the stats database (empty).
```

Development
-----------

Tests in `./item/tests` can be run with [`py.test`](https://docs.pytest.org/). The command-line option `--local-data` must be defined in order for these tests to work:

```
$ py.test --local-data=../../data/model/database item
================ test session starts ================
…
```
