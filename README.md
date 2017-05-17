Tools for accessing & maintaining the iTEM databases
====================================================

[iTEM](http://transportenergy.org) maintains two databases:

1. A **model database** of transport energy projections assembled as part of the [iTEM Workshops](https://transportenergy.org/workshops/), of which there have been two so far, with a third planned for October 2017. Because of restrictions from workshop participants, the model database is currently *not public*, but only available to iTEM workshop participants.

2. A **statistics database** to form a common, public, “best available” baseline for model calibration and projections. The statistics database is currently *under development*.

This repository contains tools for *both* databases, in *both* Python and R. The goals for these tools are that:

- iTEM participants use the tools to *access* either database and perform basic data manipulations such as retrieval, selection, and aggregation, in either Python, R (or possibly, in the future, other languages).
- Members of the [iTEM organizing group](https://transportenergy.org/participants/#organizing-group) use the tools to prepare templates for data submission, and to aggregate & clean submitted data.
- iTEM participants, if they choose, maintain code that *transparently & reproducibly* derives the iTEM variables from immediate output files of their models.
- The tools are well-tested and yield reproducible results.

Contents
--------

- `data/` — *Meta*data about the iTEM databases. Actual data is stored separately; see below.
  - `model/` — Metadata about the iTEM model database. Many of these files are in [YAML format](http://www.yaml.org/spec/1.2/spec.html) ([Wikipedia](https://en.wikipedia.org/wiki/YAML)), with more detailed comments in-line.
    - `models.yaml` — description of the [iTEM participating models & teams](https://transportenergy.org/participants/).
    - `dimensions/` — information about the [data dimensions of the model database](https://transportenergy.org/database/).
    - Other directories:
      - are named to match the keys in `models.yaml`,
      - contain model-specific metadata, including but not limited to:
        - `regions.yaml`: regional aggregation.
  - `item_config_example.yaml` — an example configuration file.
- `python/` — Python code for accessing & maintaining the database. See [`python/README.md`](https://github.com/transportenergy/database/blob/master/python/README.md).
- `R/` — R code for accessing & maintaining the database. See [`R/README.md`](https://github.com/transportenergy/database/blob/master/R/README.md).


Usage
-----

The following instructions are not language-specific. Both the Python and R tools will operate on data stored in the following way; see the language `README`s for specific information.

1. Clone this repository and/or install the code in one or both languages.

2. Create a separate directory to contain the databases. This directory should have the following structure:

  - `DATA_DIR/` (any directory of your choosing)
    - `model/`
      - `raw/` for submitted (‘raw’) data such as:
        - `MODEL.xlsx`
        - `MODEL.csv`
        - `MODEL.gdx`
      - `processed/` for processed and cleaned information, such as:
        - `MODEL.csv` — processed and cleaned data.
        - `MODEL/*` — other metadata derived from the submitted data, such as:
          - `notes.csv` — notes about the variables.
          - `regions.csv` — list of regions appearing in the submitted data.
      - `database/` for the iTEM models database in CSV format.
    - `stats/`

   Depending on the use-case, some or all of these directories may be left empty. Optionally, also create a CACHE_DIR, anywhere.

3. Copy the file `item_config_example.yaml` to `item_config.yaml` in any working directory where you intend to use this code. Edit the file (see the inline comments) so that the `path/model` key points to `DATA_DIR/model`, and (optionally) the `path/cache` key points to `CACHE_DIR`.
