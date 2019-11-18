Tools for the iTEM databases
============================
[![Build Status](https://travis-ci.org/transportenergy/database.svg?branch=master)](https://travis-ci.org/transportenergy/database)
![Codecov](https://img.shields.io/codecov/c/gh/transportenergy/database.svg)
[![Documentation Status](https://readthedocs.org/projects/transportenergy/badge/?version=latest)](https://transportenergy.readthedocs.io/en/latest/?badge=latest)

[iTEM](https://transportenergy.org) maintains two databases:

1. A **model database** of transport energy projections assembled as part of the [iTEM Workshops](https://transportenergy.org/workshops/).
   Because of restrictions from workshop participants, the model database is currently *not public*, but only available to iTEM workshop participants.

2. A **historical database** to form a common, public, “best available” baseline for model calibration and projections.
   The historical database is currently *under development*.

This repository contains tools for:

- the historical database, in Python.
- the model database from the second iTEM model intercomparison project (MIP2), in R.

Other relevant repositories:

- https://github.com/transportenergy/item_mip_data_processing contains tools for iTEM MIP3.
- https://github.com/transportenergy/metadata contains shared metadata about models and historical data sources.

The goals for these tools are that:

- iTEM participants use the tools to *access* either database and perform basic data manipulations such as retrieval, selection, and aggregation, in either Python, R (or possibly, in the future, other languages).
- Members of the [iTEM organizing group](https://transportenergy.org/participants/#organizing-group) use the tools to prepare templates for data submission, and to aggregate & clean submitted data.
- iTEM participants, if they choose, maintain code that *transparently & reproducibly* derives the iTEM variables from immediate output files of their models.
- The tools are well-tested and yield reproducible results.
- The tools are [fully documented](https://transportenergy.readthedocs.io).
