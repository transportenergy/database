Reference
*********

Repository organization
-----------------------

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
-----------

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_; use a linter to ensure compliance.
- All code must be importable from within :mod:`item`.
- Clear all cell output, execution counts, etc. from IPython notebooks committed to the repository.
