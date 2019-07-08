Tools for the iTEM databases
============================
[![Build Status](https://travis-ci.org/transportenergy/database.svg?branch=master)](https://travis-ci.org/transportenergy/database)
![Codecov](https://img.shields.io/codecov/c/gh/transportenergy/database.svg)

[iTEM](https://transportenergy.org) maintains two databases:

1. A **model database** of transport energy projections assembled as part of the [iTEM Workshops](https://transportenergy.org/workshops/).
   Because of restrictions from workshop participants, the model database is currently *not public*, but only available to iTEM workshop participants.

2. A **historical database** to form a common, public, “best available” baseline for model calibration and projections.
   The historical database is currently *under development*.

This repository contains tools for *both* databases, in *both* Python and R. The goals for these tools are that:

- iTEM participants use the tools to *access* either database and perform basic data manipulations such as retrieval, selection, and aggregation, in either Python, R (or possibly, in the future, other languages).
- Members of the [iTEM organizing group](https://transportenergy.org/participants/#organizing-group) use the tools to prepare templates for data submission, and to aggregate & clean submitted data.
- iTEM participants, if they choose, maintain code that *transparently & reproducibly* derives the iTEM variables from immediate output files of their models.
- The tools are well-tested and yield reproducible results.

Contents
--------

- `python/` — Python code for accessing & maintaining the database. See [`python/README.md`](https://github.com/transportenergy/database/blob/master/python/README.md).
  - `item/data/` — *Meta*data about the iTEM databases. Actual data is stored separately; see below.
    - `model/` — Metadata about the iTEM model database. Many of these files are in [YAML format](http://www.yaml.org/spec/1.2/spec.html) ([Wikipedia](https://en.wikipedia.org/wiki/YAML)), with more detailed comments in-line.
      - `models.yaml` — description of the [iTEM participating models & teams](https://transportenergy.org/participants/).
      - `dimensions/` — information about the [data dimensions of the model database](https://transportenergy.org/database/).
      - Other directories:
        - are named to match the keys in `models.yaml`,
        - contain model-specific metadata, including but not limited to:
          - `regions.yaml`: regional aggregation.
          - `scenarios.yaml`: descriptions of scenarios submitted to each iTEM workshop.
    - `concepts.yaml`, `measures.yaml`, `spec.yaml` — specifications of data to be submitted for for the 3rd iTEM MIP.
    - `item_config_example.yaml` — an example configuration file.
- `R/` — R code for accessing & maintaining the database. See [`R/README.md`](https://github.com/transportenergy/database/blob/master/R/README.md).


Usage
-----

The following instructions are not language-specific.
Both the Python and R tools will operate on data stored in the following way; see the language `README`s for specific information.

1. Clone this repository and/or install the code in one or both languages.

2. Create 1 or more separate directory to contain the input and output files.
   A simple way to do this is to call `item mkdirs PATH`, where `PATH` is a base directory; this will create a tree of directories.
   Use `item mkdirs --help` for more information.

3. Copy the file [`item_config_example.yaml`](https://github.com/transportenergy/database/blob/master/python/item/data/item_config_example.yaml`) to `item_config.yaml` in any working directory where you intend to use this code.
   Edit the file (see the inline comments) to point to the directories created in #2 above.

4. Use the tools through the command-line interface:

   ```
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
   ```
