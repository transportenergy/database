Glossary
********

This page gives detailed explanations of terms used elsewhere in the documentation.
Some discouraged terms are included with “scare quotes”, with preferred terms in **bold**.

.. glossary::

   Attribute
     Any information associated with an observation or group of observations. *Example:* the attribute ‘status’ might have a value of “Provisional” or “Final”, related to a statistical agency's process of publishing preliminary and then final values.

   Assumptions
     Quantities used in data processing.

   “Column”
     Refers to a *particular representation* of data, in a table.
     When describing the *structure* of data, it is often better to use **dimension** instead.
     This is because the same data can be represented in different ways (e.g. non-table formats), and tables can be organized differently; but the structure does not change.

     For example: in “wide” format with one dimension represented through multiple columns.
     In this latter case “the columns of the data” include both (a) every label for one dimension (e.g. time) and (b) the names/IDs of the other dimensions.

   Concept
     Both background concepts and specific, systematic, defined meanings. *Example:* ‘energy demand’ and ‘fuel use’.

   Conversion factor
     Used to convert between alternate measures of the same concept.
     *Example:* energy content of fuel is used to convert ‘fuel use’ from volume to energy units.

   Data
     Collective noun for of observations of specific measures for general  concepts, organized in one or more dimensions, with attributes.

     Modelled data
       Data that are produced from an existing model or calculations.

   Data processing
     Algorithms that combine raw data and assumptions to produce a dataset with greater coverage or quality; or to derive certain measures from raw data.

   Data set
     A collection of individual observations.

   Data source
     A person, agency, or web service that provides data.

     National source
       National organizations such as national statistical agencies, ministries of transport or energy, etc. who directly measure quantities or collect measurements from subsidiary organizations, and provide these as data.

     Aggregator
       An agency or person who collects and assembles data into larger data sets.
       These may include data from multiple upstream sources (such as national sources), with or without any cleaning, adjustment, or harmonization.

   Dimension
     A named list of labels or values used to organize multiple observations in a set of data. *Example:* ‘year’ (a sequential list of annual periods), ‘country’ (names or codes for countries).

   Measure
     An operational definition, including units, of a systematic concept.
     Multiple measures may exist for the same concept.
     *Example:* ‘fuel use’ may be measured in terms of the volume of fuel (litres) or its energy content (joule).

   Observation
     A single value for a measure.

   Parameter
     Used to derive one measure from another in a data processing calculation.
     *Example:* ‘occupancy of passenger vehicles’ (persons per vehicle) is used to calculate ‘passenger travel’ (in kilometres) from ‘vehicle travel’ (kilometers).

   Upstream
     Data (or software) used as an input.
     Sometimes the term “raw data” is incorrectly used for “upstream data”.
