Transport energy model projections (:mod:`item.model`)
******************************************************

On separate pages:

.. toctree::

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
