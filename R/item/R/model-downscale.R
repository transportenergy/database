# Functions used for downscaling reported data from model-reported regions to countries
#' Load the data submitted by the individual models
#'
#' Load model-submitted data into a list of data frames where each element is a single model's output (i.e., all
#' scenarios in a single data frame).
#'
#' @param model_data_folder folder where the pre-processed model output data is located
#' @details Requires that the model output data are generally cleaned and appropriately formatted, and placed into a
#'   common folder. Individual data files should be the model name plus the extension ".csv", and there should be no
#'   other csv files in the same folder.
#' @importFrom tidyr gather
#' @importFrom dplyr matches mutate
#' @importFrom magrittr "%>%"
#' @export
load_preprocessed_data <- function(model_data_folder){
  # Indicate the directory where the pre-processed model output is available
  domain <- paths[[model_data_folder]]

  if (is.null(domain)) {
    print(paste('unrecognized path:', model_data_folder))
    return()
  }
  # Put all of the data in a list, where each model is an element of the list
  data <- list()
  filenames <- list.files(domain)[endsWith(list.files(domain), "csv")]

  for(fnum in seq_along(filenames)){
    cat("Loading", filenames[fnum], "...\n")
    fqfn <- paste0(domain, "/",filenames[fnum])
    f <- sub(".csv", "", filenames[fnum])

    # Read in the data tables to the list
    data[[f]] <- read.csv(fqfn, comment.char = COMMENT_CHAR, stringsAsFactors=FALSE,
                          na.strings = c( "", "NA")) %>%
      # apply tidy (internal item function) and melt (gather) the years
      tidy() %>%
      gather(year, value, matches(YEAR_PATTERN)) %>%
      # year needs to be numeric for subsequent interpolation to work
      mutate(year=as.numeric(year))
  }
  return(data)
}

#' Apply corrections to pre-processed data
#'
#' Addresses errors and omissions in submitted model data loaded by \code{\link{load_preprocessed_data}} prior to
#' performing any data processing. Where necessary, corrections are performed by calling model-specific functions. This
#' function also performs a number of processing steps that are optional but default to true. These include: subsetting
#' only quantity flow variables (the methods assume that the components to all indicator variables are reported as
#' quantity flows, and can be re-computed post-hoc from various levels of regional aggregation), removing "All"
#' categories when the consituent components are available (\code{\link{remove_redundant_alls}}), interpolating years
#' where necessary for harmonized reporting years, dropping missing values (the alternative is setting them to zero),
#' and aggregating redundant categories (as category re-assignment may cause multiple values with the same ID info).
#'
#' @param model_data_list list of data frames with model-specific data
#' @param subset_quantity_flows logical (default = TRUE) indicating whether to subset only quantity flow variables
#' @param remove_redundant_alls logical (default = TRUE) indicating whether to remove observations with "All" that could
#'   be calculated instead by adding provided components. These "All" values should not be downscaled.
#' @param interpolate_years logical (default = TRUE) indicating whether to interpolate years.
#' @param drop_na_values logical (default = TRUE) indicating whether to drop observations with no value in model-
#'   submitted data. If FALSE, missing values are set to zero.
#' @param aggregate_redundant_categories logical (default = TRUE) indicating whether to add up categories that are
#' redundant (i.e., all ID information the same), which generally result from re-setting variables from model-
#' reported data to more aggregate categories.
#' @details To apply model-specific functions, this function searches for a correction function containing each model
#'   name in the list (i.e., "correct_" + model name). This step is applied prior to all others. The interpolation
#'   function does not extrapolate, so the data from any model does not necessarily include all iTEM analysis years. In
#'   its present form, this function does not call additional functions to compute quantity flows from indicator
#'   variables, though such capacity may be added for an expanded variable set. For example, to process fuel prices,
#'   fuel expenditures would be calculated as reported prices times consumption.
#' @importFrom assertthat assert_that
#' @importFrom dplyr bind_rows mutate group_by ungroup
#' @importFrom magrittr "%>%"
#' @export
prepare_preprocessed_data <- function(model_data_list,
                                      subset_quantity_flows = TRUE,
                                      remove_redundant_alls = TRUE,
                                      interpolate_years = TRUE,
                                      drop_na_values = TRUE,
                                      aggregate_redundant_categories = TRUE, ...){
  assert_that(is.list(model_data_list))
  assert_that(is.logical(subset_quantity_flows))
  assert_that(is.logical(remove_redundant_alls))
  assert_that(is.logical(interpolate_years))
  assert_that(is.logical(drop_na_values))
  assert_that(is.logical(aggregate_redundant_categories))

  if(subset_quantity_flows){
    print("Note: Only retaining quantity flow variables from submitted model data.")
    # load the variable type mapping, and derive a vector of quantity flow variables to be retained
    flow_variables <- get_variable_mapping(...)
    flow_variables <- flow_variables$variable[flow_variables$variable_type == "quantity"]
  }

  for(model in names(model_data_list)){
    # Standardize on a region name for the global/world region. Setting to "All" allows removal of redundant reporting
    model_data_list[[model]] <- model_data_list[[model]] %>%
      mutate(region = if_else(region %in% c("World", "Wor", "Global"), "All", region))
    # Apply any model-specific correction functions, as necessary
    if( exists(paste0("correct_", model), mode = "function")){
      print( paste0( "Applying model-specific corrections to data from model: ", model ))
      correction_function <- get( paste0("correct_", model))
      model_data_list[[model]] <- correction_function(model_data_list[[model]])
    }
    # Subset quantity flows, if indicated
    if(subset_quantity_flows){
      model_data_list[[model]] <- subset(model_data_list[[model]],
                                         variable %in% flow_variables)
    }
    # Remove redundant "All" values of selected ID variables, if indicated
    if(remove_redundant_alls){
      model_data_list[[model]] <- remove_redundant_alls(model_data_list[[model]])
    }
    # Interpolate the years provided, if indicated
    if(interpolate_years){
      print( paste0( "Interpolating years from model: ", model ))
      model_data_list[[model]] <- model_data_list[[model]] %>%
        group_by(scenario, region, variable, mode, technology, fuel) %>%
        mutate(value = approx_fun(year, value)) %>%
        ungroup()
    }
    # Either drop NA values or or set them to zero
    if(drop_na_values){
      model_data_list[[model]] <- model_data_list[[model]] %>%
        filter(!is.na(value))
    } else {
      model_data_list[[model]] <- model_data_list[[model]] %>%
        mutate(value = if_else(is.na(value), 0, value))
    }
    # Aggregate redundant quantities, if indicated
    if( aggregate_redundant_categories){
      #For any model-reported categories that were re-assigned to a more aggregate categories (e.g., from different
      #sizes of trucks (LHDT, MHDT, HHDT) to trucks (HDT)), then these should be aggregated. If no such re-assignments
      #took place, then this step won't do anything. First, make sure that only quantity variables are subsetted, as we
      #don't want to be adding indicator variables
      assert_that(subset_quantity_flows)
      model_data_list[[model]] <- model_data_list[[model]] %>%
        group_by_(.dots = lapply(ITEM_ID_COLUMNS, as.symbol)) %>%
        summarise( value = sum(value)) %>%
        ungroup()
    }
  } # end for(model in names(model_data_list))
  return(model_data_list)
} # end function

#' Downscale annual flow variables from model regions to countries
#'
#' Performs a merge of (1) pre-processed and corrected model output (by native model region) from
#' \code{\link{prepare_preprocessed_data}}, (2) country-within-model-region shares of downscaling proxies from
#' \code{\link{compute_country_shares}}, and (3) assignment of a nation-level socioeconomic realization for each model
#' and scenario from \code{\link{assign_socioeconomic_scenario}}. Returns a list of model-specific dataframes with all
#' quantity (i.e., annual flow) variables reported at the country level.
#'
#' @param model_data_list list of model-specific dataframes with cleaned and pre-processed output
#' @param model_socio_list list of model-specific dataframes assigning each submitted scenario to a country-level
#'   socioeconomic scenario
#' @param country_share_list list of model-specific lists of downscaling proxy dataframes indicating country-
#'   within-region shares
#' @param collapse_list logical (default = TRUE) indicating whether to return output as a single data frame (TRUE) or a
#'   list of model-specific data frames (FALSE).
#' @details Takes in three lists; the named elements of each of these lists should be the model names, and they must
#'   be standardized. All models and scenarios in \code{model_data_list} must be available in \code{model_socio_list},
#'   though there is no problem if the latter contains additional models and/or scenarios. Similarly, all models and
#'   socioeconomic realizations from joining \code{model_data_list} and \code{model_socio_list} must be available in
#'   \code{country_share_list}, though the latter may contain additional nation-level socioeconomic realizations.
#'   Finally, all reported quantity variables must be assigned to a downscaling proxy in \code{variable_ds_proxy_fn}
#'   that is also available in \code{country_share_list}.
#' @importFrom assertthat assert_that
#' @importFrom dplyr right_join left_join select mutate filter select_ arrange_ bind_rows group_by_ summarise ungroup
#' @importFrom magrittr "%>%"
#' @export
downscale_flow_variables <- function(model_data_list,
                                     model_socio_list,
                                     country_share_list,
                                     collapse_list = TRUE, ...){
  assert_that(is.list(model_data_list))
  assert_that(is.list(model_socio_list))
  assert_that(is.list(country_share_list))
  assert_that(is.logical(collapse_list))

  # load the variable-to-downscaling-proxy mapping file
  variable_ds_proxy <- get_variable_mapping(...) %>%
    filter(variable_type == "quantity") %>%
    select(-variable_type)
  # generate the new list with country-level model output, and indicate the column names
  downscaled_data_list <- list()
  for( model_name in names(model_data_list)){
    # Assign an empty list to each model
    downscaled_data_list[[model_name]] <- list()
    for(proxy_name in names(country_share_list[[model_name]])){
      print(paste0("Downscaling quantity flows from model ", model_name,
                   " assigned to downscaling proxy ", proxy_name))
      # country share data: keep only relevant socioeconomic realization(s),
      # repeat as necessary by model scenario
      country_share_list[[model_name]][[proxy_name]] <-
        country_share_list[[model_name]][[proxy_name]] %>%
        right_join(model_socio_list[[model_name]], by="socio")

      # Determine the "by" argument for joining country shares with model output
      join_fields <- names(country_share_list[[model_name]][[proxy_name]])[
        !names(country_share_list[[model_name]][[proxy_name]]) %in% c("socio", "iso", "value") ]

      # Perform the merge, replacing native model regions with countries
      downscaled_data_list[[model_name]][[proxy_name]] <-
        model_data_list[[model_name]] %>%
        left_join(variable_ds_proxy, by = "variable" ) %>%
        filter(ds_proxy == proxy_name) %>%
        left_join(country_share_list[[model_name]][[proxy_name]],
                  by = join_fields, suffix = c("_reg_total", "_country_share")) %>%
        filter(!is.na(iso)) %>%
        mutate(value = value_reg_total * value_country_share) %>%
        select_(.dots = lapply(DS_DATA_COLUMNS, as.symbol))
    } #end for(proxy_name in names(country_share_list[[model_name]]))
    # Bind the different proxies within each model
    downscaled_data_list[[model_name]] <-
      do.call(bind_rows, downscaled_data_list[[model_name]]) %>%
      arrange_(.dots = lapply(DS_DATA_COLUMNS, as.symbol))
  } # end for( model_name in names(model_data_list))
  if(collapse_list){
    downscaled_data <- do.call(bind_rows, downscaled_data_list)
    return(downscaled_data)
  } else {
    return(downscaled_data_list)
  }
} # end function

#' Compute country shares for model output by native model region
#'
#' Compute country-with-model-region shares for models, downscaling proxies, nation-level socioeconomic realizations,
#' and years. Takes in list of model data from \code{\link{prepare_preprocessed_data}}, each model's country-to-region
#' mapping from \code{\link{get_country_region_map}}, and country-level downscaling proxy data from
#' \code{\link{generate_ds_proxy_data}}. Returns a list with all combinations of model, downscaling proxy, country-level
#' socioeconomic realization, and year.
#'
#' @param model_data_list list of model output data that has been cleaned, pre-processed, and prepared (i.e., corrected)
#' @param ds_proxy_data list of downscaling proxy dataframes
#' @param save_output logical indicating whether to save the output of this function
#' @param create_dir logical indicating whether to create a new directory for the output (if one with the expected name
#'   doesn't already exist)
#' @param output_dir directory in which to save the output
#' @details Returns a list of models, each element of which is a list of downscaling proxy dataframes, each of which
#'   indicates country-within-model-region shares, to be used by \code{\link{downscale_flow_variables}} in order to
#'   downscale region-level model output to the country level. Returned data are filtered to the years reported by each
#'   model, and include all possible nation-level socioeconomic realizations.
#' @importFrom assertthat assert_that
#' @importFrom dplyr group_by_ summarise select mutate ungroup filter left_join rename
#' @importFrom magrittr "%>%"
#' @importFrom readr write_csv
#' @export
compute_country_shares <- function(model_data_list,
                                   ds_proxy_data = generate_ds_proxy_data(),
                                   save_output = TRUE, create_dir = TRUE,
                                   output_dir = DS_OUTPUT_DIR){
  assert_that(is.list(model_data_list))
  assert_that(is.list(ds_proxy_data))
  assert_that(is.logical(save_output))
  assert_that(is.logical(create_dir))
  assert_that(is.character(output_dir))

  # The output is a list of models, each of which is a list of downscaling proxies.
  output_list <- list()
  # Process each model separately in a for loop
  for(model_name in names(model_data_list)){
    # get the country-to-region mapping for the given model
    region_map <- get_country_region_map(model_name)
    # figure out which years this will be written out for
    model_years <- sort(unique(model_data_list[[model_name]]$year))
    # each model in the list will also be a list of downscaling proxies
    output_list[[model_name]] <- list()
    for(ds_proxy in names(ds_proxy_data)){
      ds_proxy_name <- unique(ds_proxy_data[[ds_proxy]]$ds_proxy)
      print(paste0("Computing country-within-region shares for model: ",
                   model_name, ", and proxy: ", ds_proxy_name))
      ds_proxy_region <- ds_proxy_data[[ds_proxy]] %>%
        filter(year %in% model_years) %>%
        left_join(region_map, by = "iso") %>%
        na.omit()
      # The group_by columns may include mode; need to keep this flexible to column names
      group_columns <- names(ds_proxy_region)[!names(ds_proxy_region) %in% c("value", "iso")]
      # Convert character vector to list of symbols
      dots <- lapply(group_columns, as.symbol)
      ds_proxy_region <- ds_proxy_region %>%
        group_by_(.dots = dots) %>%
        summarise(reg_total = sum(value)) %>%
        ungroup()
      output_list[[model_name]][[ds_proxy_name]] <- ds_proxy_data[[ds_proxy]] %>%
        filter(year %in% model_years) %>%
        left_join(region_map, by="iso") %>%
        left_join(ds_proxy_region, by = group_columns) %>%
        mutate(value = value / reg_total) %>%
        # Get rid of any missing values from dividing by zero (assuming these are all too small to matter)
        mutate(value = if_else(is.na(value), 0, value)) %>%
        select(-reg_total) %>%
        # The socioeconomic scenario is named "socio"
        rename(socio = scenario)
      # write the data out, if requested
      if(save_output){
        # Create the directory if called for
        if(create_dir) dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
        write_csv(output_list[[model_name]][[ds_proxy_name]],
                  path = paste0(output_dir, "/country_shares_", model_name, "_", ds_proxy_name, ".csv"))
      } # end if(save_output)
    } # end for(ds_proxy in names(ds_proxy_data))
  } # end for(model_name in model_names)
  return(output_list)
} #end function

#' Assign country-level socioeconomic realization to each model+scenario
#'
#' Takes in list of model output data from \code{\link{prepare_preprocessed_data}} and returns a list of model-
#' specific dataframes mapping model scenarios to named nation-level socioeconomic realizations. Default behavior
#' is to compute these assignments by minimizing sum of squared errors in future GDP ratios by model region and
#' time period.
#'
#' @param model_data_list list of data tables of model-specific pre-processed, prepared data
#' @param method method used for assigning scenarios. SSE: default behavior; minimize sum of squared errors in future
#'   ratios of variable indicated, by year and model region. exogenous: use exogenously provided assignments between
#'   model+scenario and nation-level socioeconomic realization for downscaling model output.
#' @param variable variable to use in determining the socioeconomic assignment; can be population or gdp
#' @details Returns a list of dataframes where each model is an element. Data frames assign model's scenarios
#' to a country-level socioeconomics file.
#' @importFrom assertthat assert_that
#' @importFrom yaml yaml.load_file
#' @importFrom dplyr full_join group_by summarise select mutate rename ungroup filter left_join slice
#' @importFrom magrittr "%>%"
#' @importFrom data.table rbindlist
#' @export
assign_socioeconomic_scenario <- function( model_data_list,
                                           method = "SSE",
                                           SSE_variable = "PPP-GDP"){
  assert_that(is.list(model_data_list))
  assert_that(method %in% c("exogenous", "SSE"))
  assert_that(SSE_variable %in% c("PPP-GDP", "Population"))

  output_list <- list()
  if(SSE_variable == "PPP-GDP") country_data <- generate_ds_proxy_data()$ds_proxy_gdp
  if(SSE_variable == "Population") country_data <- generate_ds_proxy_data()$ds_proxy_population
  if(method == "exogenous") print("Using exogenous assignments from model/scenario to country-level socio scenario")
  for(model_name in names(model_data_list)){
    if(method == "exogenous"){
      scenario_assignment <- load_data_file(paste0("model/",model_name,"/scenarios.yaml"), quiet = TRUE) %>%
        rbindlist(idcol = "scenario") %>%
        select(scenario, socio)
    } # end if(method == "exogenous")
    if(method == "SSE"){
      print(paste0("Determining country-level socioeconomic scenarios for model: ", model_name))
      # Get the country-to-region assignments for the given model
      region_assignment <- get_country_region_map(model_name)
      # Need to figure out if the model provided socioeconomic information. If not, the data frame can be written here
      if(!SSE_variable %in% unique( model_data_list[[model_name]]$variable)){
        scenario_assignment <- data.frame(scenario = unique(model_data_list[[model_name]]$scenario),
                                          socio = DS_DEFAULT_SCENARIO,
                                          stringsAsFactors = FALSE)
      } else {
        model_data <- subset( model_data_list[[model_name]], variable == SSE_variable) %>%
          # Filter out any years with missing values
          filter(!is.na(value)) %>%
          # only do the assessment on 2010 and later, as this is the base year for the socioeconomics
          filter(year >= 2010) %>%
          filter(region %in% unique(region_assignment$region)) %>%
          select(model, scenario, region, year, value)
        # Aggregate the country-level socio data by the model's regions
        socio_data <- country_data %>%
          left_join(region_assignment, by = "iso") %>%
          filter(!is.na(region)) %>%   #not all countries are assigned to a region
          filter(year %in% model_data$year) %>%
          select(-ds_proxy) %>%
          group_by(scenario, region, year) %>%
          summarise(value = sum(value)) %>%
          ungroup()
        # Merge the aggregated country-level socio data with the model's output
        merged_data <- socio_data %>%
          full_join(model_data, by = c("region", "year"), suffix = c("_socio","_model")) %>%
          # some models may have mapped regions that aren't actually in their output. These are missing values here.
          na.omit()
        # Subset the base-year data to merge back in, in order to compute growth ratios from the base year
        # 2010 is the base year for the SSPs (may be a future year for some models)
        base_data <- subset(merged_data, year == min(year)) %>%
          rename(base_value_socio = value_socio) %>%
          rename(base_value_model = value_model) %>%
          select(model, scenario_socio, scenario_model, region, base_value_socio, base_value_model)
        # Compute the ratios
        merged_data <- left_join( merged_data, base_data,
                                  by = c("model", "scenario_socio", "scenario_model", "region")) %>%
          mutate( value_socio = value_socio / base_value_socio ) %>%
          mutate( value_model = value_model / base_value_model) %>%
          # If a model reported a region but had zero values, this returns a missing value. Just drop the obs.
          na.omit() %>%
          filter( year != min(year)) %>%
          # Compute the squared errors for each observation, and aggregate to compute the sum of squared errors
          mutate(SSE = (value_socio - value_model)^2) %>%
          select( model, region, year, scenario_socio, scenario_model, value_socio, value_model, SSE)
        SSE_data <- merged_data %>%
          group_by(scenario_socio, scenario_model) %>%
          summarise(SSE = sum(SSE)) %>%
          ungroup() %>%
          group_by(scenario_model) %>% slice(which.min(SSE)) %>%
          ungroup()
        scenario_assignment <- data.frame(scenario = SSE_data$scenario_model,
                                          socio = SSE_data$scenario_socio,
                                          stringsAsFactors = FALSE)
      } #end else; if(!SSE_variable %in% unique( model_data_list[[model_name]]$variable))
    } # end if(method == "SSE")
    output_list[[model_name]] <- scenario_assignment
  } # end for(model_name in names(model_data_list))
  return(output_list)
} # end function

#' Generate country-level data for each socioeconomic realization and downscaling proxy
#'
#' Takes in file paths to country-level data that is used to construct downscaling proxy datasets for any number of
#' country-level socioeconomic realizations, in all time periods. Input socioeconomic data must include all future
#' analysis years; these data are used to expand but other proxy data from a given base year to all iTEM analysis years.
#' Returns a list of downscaling proxy dataframes.
#'
#' @param pop_data_fn file name of data with population by scenario, country, year (including future iTEM years)
#' @param gdp_data_fn file name of data with GDP by scenario, country, year (including future iTEM years)
#' @param co2_data_t0_fn file name of data with CO2 emissions by country, for a base year
#' @param transportenergy_data_t0_fn file name of data with transportation energy consumption data by country, for a
#'   base year. May include mode-level detail.
#' @param use_modal_detail logical indicating whether to determine mode-specific proxy values. If false, a single proxy
#'   will be calculated for the whole transportation sector.
#' @param apply_modal_elasticities logical indicating whether to differentiate income elasticities by mode. If true,
#'   exogenous assumptions are used. If false, all modes are assigned an income elasticity of 1.
#' @param save_output indicate whether to save the output of this function
#' @param create_dir indicate whether to create a new directory if the specified one does not already exist
#' @param output_dir file path where output of this function is saved
#' @details The downscaling proxy data generated by this function are assumed to apply to all models; i.e., elasticities
#'   linking future GDP growth to future changes in the base-year proxy data do not differ by model.
#' @importFrom assertthat assert_that
#' @importFrom tidyr gather
#' @importFrom dplyr bind_rows mutate group_by filter select matches rename full_join left_join if_else
#' @importFrom magrittr "%>%"
#' @importFrom readr write_csv
generate_ds_proxy_data <- function(pop_data_fn = "downscale/SSP_Population.csv",
                                   gdp_data_fn = "downscale/SSP_GDP_PPP.csv",
                                   co2_data_t0_fn = "downscale/CDIAC_CO2_ctry.csv",
                                   transportenergy_data_t0_fn = "downscale/IEA_trn_ctry.csv",
                                   use_modal_detail = TRUE,
                                   apply_modal_elasticities = TRUE,
                                   save_output = TRUE, create_dir = TRUE,
                                   output_dir = DS_OUTPUT_DIR, ...){
  assert_that(is.character(pop_data_fn))
  assert_that(is.character(gdp_data_fn))
  assert_that(is.character(co2_data_t0_fn))
  assert_that(is.character(transportenergy_data_t0_fn))
  assert_that(is.logical(use_modal_detail))
  assert_that(is.logical(apply_modal_elasticities))
  assert_that(is.logical(save_output))
  assert_that(is.logical(create_dir))
  assert_that(is.character(output_dir))
  # For population and GDP data, we just need to re-format the tables and extract the SSP name
  ds_proxy_population <- load_data_file(pop_data_fn, quiet = TRUE) %>%
    gather(year, value, matches(YEAR_PATTERN)) %>%
    mutate(scenario = substr(SCENARIO, 1, 4)) %>%
    mutate(year = as.numeric(year)) %>%
    filter(year %in% ITEM_YEARS) %>%
    mutate(iso = toupper(REGION)) %>%
    mutate(ds_proxy = "POPULATION") %>%
    select(ds_proxy, scenario, iso, year, value)
  ds_proxy_gdp <- load_data_file(gdp_data_fn, quiet = TRUE) %>%
    gather(year, value, matches(YEAR_PATTERN)) %>%
    mutate(scenario = substr(SCENARIO, 1, 4)) %>%
    mutate(year = as.numeric(year)) %>%
    filter(year %in% ITEM_YEARS) %>%
    mutate(iso = toupper(REGION)) %>%
    mutate(ds_proxy = "GDP") %>%
    select(ds_proxy, scenario, iso, year, value)
  # For co2 and transportenergy, use GDP growth ratios to expand available (base year) data
  # to all iTEM years
  gdp_baseyear_data <- subset( ds_proxy_gdp, year == BASEYEAR) %>%
    select(-year) %>%
    rename(base_gdp = value)
  gdp_growth_ratios <- ds_proxy_gdp %>%
    rename(gdp = value) %>%
    left_join(gdp_baseyear_data, by = c("ds_proxy", "scenario", "iso")) %>%
    mutate(growth_ratio = gdp/base_gdp) %>%
    select(scenario, iso, year, growth_ratio)
  co2_baseyear_data <- load_data_file(co2_data_t0_fn, quiet = TRUE) %>%
    rename(base_value = value) %>%
    mutate(iso = toupper(iso)) %>%
    select(iso, base_value) %>%
    filter(iso %in% gdp_growth_ratios$iso)
  ds_proxy_co2 <- gdp_growth_ratios %>%
    left_join(co2_baseyear_data, by = "iso") %>%
    # Set any countries in the GDP but not CO2 data to zero
    mutate(base_value = if_else(is.na(base_value), 0, base_value)) %>%
    mutate(ds_proxy = "CO2") %>%
    mutate(value = base_value * (growth_ratio ^ DS_GDP_ELAST_CO2)) %>%
    select(ds_proxy, scenario, iso, year, value)
  transportenergy_data_t0 <- load_data_file(transportenergy_data_t0_fn, quiet = TRUE) %>%
    prepare_transportenergy_t0_data(use_modal_detail = use_modal_detail) %>%
    filter( iso %in% gdp_growth_ratios$iso)
  ds_proxy_transportenergy <- gdp_growth_ratios %>%
    filter( iso %in% transportenergy_data_t0$iso) %>%
    full_join(transportenergy_data_t0, by = "iso") %>%
    mutate(base_value = if_else(is.na(base_value), 0, base_value)) %>%
    mutate(ds_proxy = "TRANSPORTENERGY") %>%
    mutate(value = base_value * growth_ratio)  # default assumption is elasticity of 1
    if( apply_modal_elasticities){
      mode_GDP_elasticity <- load_data_file( "downscale/mode_GDP_elasticity.csv", quiet = TRUE)
      ds_proxy_transportenergy <- ds_proxy_transportenergy %>%
        left_join( mode_GDP_elasticity, by = "mode") %>%
        mutate( value = base_value * growth_ratio ^ elasticity )
    }
  ds_proxy_transportenergy <- ds_proxy_transportenergy %>%
    select(ds_proxy, scenario, iso, mode, year, value)
  proxy_list <- list( ds_proxy_population = ds_proxy_population,
                      ds_proxy_gdp = ds_proxy_gdp,
                      ds_proxy_co2 = ds_proxy_co2,
                      ds_proxy_transportenergy = ds_proxy_transportenergy)
  # If indicated, write the data out to an intermediate output directory
  if(save_output){
    # Create the output directory, if indicated
    if(create_dir) dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
    for(proxy_table in names(proxy_list)){
      write_csv(proxy_list[[proxy_table]],
                path = paste0(output_dir, "/",names(proxy_list[proxy_table]), ".csv"))
    }
  }
  return(proxy_list)
}

#' Get the country-to-region mapping for a given model
#'
#' @param model_name name of model whose country-to-region mapping is to be returned
#' @details Takes in yaml lists of countries in each model region, and returns a data frame with two columns: iso and
#'   region
#' @importFrom assertthat assert_that
#' @importFrom yaml yaml.load_file
#' @importFrom dplyr rename
#' @importFrom magrittr "%>%"
#' @importFrom data.table rbindlist
get_country_region_map <- function(model_name){
  assert_that(is.character(model_name))

  region_assignment <- load_data_file(paste0("model/",model_name,"/regions.yaml"), quiet = TRUE)
  # strip any meta-info other than the country names
  region_assignment <- lapply(region_assignment, function(x){x <- x['countries']}) %>%
    rbindlist(idcol = "region") %>%
    rename(iso = countries)
  return(region_assignment)
} # end function

#' Generate base-year transportation dataset from which to construct the transport energy downscaling proxy
#'
#' Perform some pre-processing of the base-year transportation data that will be expanded to all years and used as a
#' downscaling proxy in \code{\link{generate_ds_proxy_data}}.
#'
#' @param datafile data table with transportation energy consumption
#' @param mode_mapping_file mapping from mode in the transportation energy data to the iTEM modes
#' @details The transportation proxy data has modes which may or may not be used, and if they are used, they are
#'   somewhat different from the iTEM modes. This function performs the modal pre-processing to construct a useful
#'   base-year dataset which can be expanded to all iTEM years for each socioeconomic realization.
#' @importFrom assertthat assert_that
#' @importFrom tidyr complete
#' @importFrom dplyr full_join group_by summarise select mutate rename ungroup
#' @importFrom magrittr "%>%"
prepare_transportenergy_t0_data <- function( country_data,
                                             use_modal_detail = TRUE,
                                             mode_mapping_fn = "downscale/map_mode_IEA.csv", ...){
  assert_that(is.data.frame(country_data))
  assert_that(is.logical(use_modal_detail))
  assert_that(is.character(mode_mapping_fn))

  # load and pre-process the country-level data
  country_data <- country_data %>%
    mutate(iso = toupper(iso)) %>%
    rename(base_value = value)

  # Aggregate all modes, for downscaling data from models only reporting mode "All"
  country_data_allmodes <- country_data %>%
    group_by(iso) %>%
    summarise(base_value = sum(base_value)) %>%
    ungroup() %>%
    mutate(mode = "All") %>%
    select(iso, mode, base_value)
  #If no modal detail is requested, this is the final output of this function
  if(!use_modal_detail){
    return(country_data_allmodes)
  } else {
    # load the mode mapping file
    mode_mapping <- load_data_file(mode_mapping_fn, quiet = TRUE)
    country_data <- country_data %>%
      # combine international and domestic air which are not separated in iTEM
      mutate(FLOW = if_else(FLOW %in% c("AVBUNK", "DOMESAIR"), "AIR", FLOW)) %>%
      select(iso, FLOW, base_value) %>%
      group_by(iso, FLOW) %>%
      summarise(base_value = sum(base_value)) %>%
      ungroup() %>%
      full_join(mode_mapping, by = "FLOW") %>%
      select(iso, mode, base_value) %>%
      # Fill this out to all combinations of country x mode
      complete(iso, mode = unique(mode), fill = list(base_value = 0)) %>%
      bind_rows(country_data_allmodes)
    return(country_data)
  }
}

#' Aggregate across selected categories of quantity flow data, looping through all permutations
#'
#' Inputs are a data frame with model data, and a character vector of ID variables to loop through. All possible
#' permutations of the variables provided are returned in the output, with no redundant categories written out.
#' Returns the intial data frame with permutations appended.
#'
#' @param input_data data table with quantity (flow) variables
#' @param variables character string indicating the variables to loop over
#' @details The method implemented here assumes that all itemized elements of each variable to add to the total. Any
#'   excluded elements will not be part of the reported total, and redundant categories (e.g., gasoline,
#'   total liquid fuels) will be double counted.
#' @importFrom assertthat assert_that
#' @importFrom dplyr group_by_ summarise ungroup bind_rows
#' @importFrom magrittr "%>%"
#' @export
aggregate_all_permutations <- function(input_data, variables = ITEM_IDVARS_WITH_ALLS){
  assert_that(is.data.frame(input_data))
  assert_that(is.character(variables))

  output_data <- input_data
  group_columns <- names(output_data)[ names(output_data) != "value"]
  dots <- lapply(group_columns, as.symbol)

  for(var in variables){
    print(paste0("Collapsing ", var, " to All and appending"))
    # Where this variable is already "All", exclude from the aggregation (would result in double counting)
    # Exclude missing values
    output_thisvar <- output_data[ output_data[[var]] != "All" & !is.na(output_data[[var]]),]
    if(nrow(output_thisvar) > 0){
      output_thisvar[[var]] <- "All"
      output_thisvar <- output_thisvar %>%
        group_by_(.dots = dots) %>%
        summarise(value = sum(value)) %>%
        ungroup()
      output_data <- bind_rows(output_data, output_thisvar)
    }
    # the output of each loop is passed to the input of the next loop, generating all permutations
  }
  return(output_data)
}

#' Get internal variable mapping assignments (with option to pull an external file instead)
#'
#' @param mapping_fn file path and name of variable mapping
#' @details Takes in a csv table with variables and associated categories. Defaults to the one provided with the item
#' package, but can be set to a different one.
#' @importFrom assertthat assert_that
get_variable_mapping <- function(mapping_fn = "downscale/variable_ds_proxy.csv"){
  assert_that(is.character(mapping_fn))
  variable_mapping <- load_data_file(mapping_fn, quiet = TRUE)
  return(variable_mapping)
}

#' Remove redundant "All" values from selected variables (columns)
#'
#' An "All" value for an ID column may be the only data available, or it may be derived from the sum of available
#' components. Except for diagnostic purposes, "All" and its sub-components should never be downscaled independently due
#' to potentially different proxies. Instead, where component-level data are available, "All" should be computed
#' post-hoc as the sum of the components. This function drops redundant "All" values (i.e., values that could be
#' computed from provided components.
#'
#' Note that the method assumes that if any components are provided for a given variable that has "All" reported, then
#' all necessary components to re-calcualate the reported "All" value are provided. However this condition is not
#' checked numerically, and the method will result in a loss of data if a model provided a category called "All", and
#' some but not all of its sub-components.
#'
#' @param data data frame with model-reported quantity variables
#' @param variables data frame with model-reported quantity variables
#' @details
#' @importFrom assertthat assert_that
#' @importFrom dplyr anti_join
remove_redundant_alls <- function(data, variables = ITEM_IDVARS_WITH_ALLS){
  assert_that(is.data.frame(data))
  assert_that(is.character(variables))

  for(idvar in variables){
    other_idvars <- ITEM_ID_COLUMNS[which(ITEM_ID_COLUMNS != idvar)] #"by" variables for anti-join
    data_na <- data[ is.na(data[[idvar]]), ]  #Need to keep all observations with NA for this variable
    data_no_alls <- data[ data[[idvar]] != "All" & !is.na(data[[idvar]]), ]
    data_alls <- data[ data[[idvar]] == "All" & !is.na(data[[idvar]]), ] %>%
      anti_join(data_no_alls, by = other_idvars)
    data <- bind_rows(data_na, data_no_alls, data_alls)
  }
  return(data)
}

#' Extract global data from model-specific data list to a data frame.
#'
#' Simple wrapper function to extract global data (region == "All") from list of model output data. Returns global-only
#' data if executed after (\code{\link{remove_redundant_alls}}), as called from
#' (\code{\link{prepare_preprocessed_data}})
#'
#' @param model_data list of model-specific data frames from which to extract the global data
#' @param input_region_col name of the region column in the input data
#' @param output_region_col name of the region column in the output (return) data
#' @details Modeling teams may provide some data at the global level only, i.e., with no regional detail available. Such
#'   data is neither downscaled to countries/regions nor dropped. This function generates a data frame with global-only
#'   data from all models that can be binded to other data frames with regional detail.
#' @importFrom assertthat assert_that
#' @importFrom dplyr bind_rows
#' @export
extract_global_data_to_df <- function(model_data, input_region_col = "region", output_region_col = "region"){
  assert_that(is.list(model_data))
  assert_that(is.character(input_region_col))
  assert_that(is.character(output_region_col))

  global_data <- do.call(
    bind_rows,
    lapply(model_data, function(x){
      x <- x[x[[input_region_col]] == "All", ]
      })
  )
  names(global_data)[ names(global_data) == input_region_col] <- output_region_col
  return(global_data)
}

# aggregate_regions()
# compute_indicator_variables()
# get_indicator_variable_derivations()
# export_data()

