Transport energy model projections (:mod:`item.model`)
******************************************************

- The `transportenergy/item_mip_data_processing <https://github.com/transportenergy/item_mip_data_processing>`_ repository contains R scripts for iTEM **MIP3** (2019–2020).
- The `transportenergy/database <https://github.com/transportenergy/database>`_ repository contains:

  - R scripts for the iTEM **MIP2** (2016–2017).
  - Python tools for preparing data submission templates and plotting mode data.

On separate pages:

.. toctree::

   model/mip2
   model/common
   model/dimensions
   model/plot

.. automodule:: item.model
   :members:

   The sub-modules of :mod:`item.model` read from the Excel reporting templates (BP, ExxonMobil, IEA, ITF, and MESSAGE) or GAMS GDX file (EPPA5), and perform manipulations specific to each model.

   .. autosummary::

      get_model_names
      get_model_info
      load_model_regions
      load_model_scenarios
      load_model_data
