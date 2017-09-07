# Functions used for downscaling reported data from model-reported regions to countries
#' Load the data submitted by the individual models
#'
#' @param model_data_folder folder where the pre-processed model output data is located
#' @details Requires that the model output data are generally cleaned and appropriately formatted,
#' and placed into a common folder.
#' Individual data files should be the model name plus the extension ".csv",
#' and there should be no other csv files in the same folder.
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

#' Apply corrections to pre-processed data, with options to unlist and interpolate years
#'
#' @param data list of data frames with model-specific data
#' @param collapse_list logical indicating whether to collapse the output data into a single data
#' frame, or keep it as a list of data frames
#' @param interpolate_years logical indicating whether to interpolate years (no extrapolation option)
#' @details Applies model-specific functions, matching the named element of the list to a
#' corresponding function containing the same string ("correct_" + model name). Also interpolates
#' years, where expected years are not provided.
#' @importFrom assertthat assert_that
#' @importFrom dplyr bind_rows mutate group_by ungroup
#' @importFrom magrittr "%>%"
prepare_preprocessed_data <- function(data, collapse_list = FALSE, interpolate_years = TRUE){
  assert_that(is.list(data))
  assert_that(is.logical(collapse_list))
  assert_that(is.logical(interpolate_years))
  for(model in names(data)){
    # Rename world as global, where applicable
    data[[model]] %>%
      mutate(region = sub("World", "Global", region))
    # Apply any model-specific correction functions, as necessary
    if( exists(paste0("correct_", model), mode = "function")){
      print( paste0( "Applying model-specific corrections to data from model: ", model ))
      correction_function <- get( paste0("correct_", model))
      data[[model]] <- correction_function(data[[model]])
    }
    # Interpolate the years
    # Note: Using rule=1 (always, no other option provided) to avoid extrapolating beyond given years.
    # Note: this was tested doing interpolations separately for each element in the list, and
    # together in a single data frame, and it didn't matter wrt system time.
    if(interpolate_years){
      print( paste0( "Interpolating years from model: ", model ))
      data[[model]] %>%
        group_by(scenario, region, variable, mode, technology, fuel) %>%
        mutate(value = approx_fun(year, value)) %>%
        ungroup()
    } # end if(interpolate_years)
  } # end for(model in names(data))
  # If collapse_list, bind the rows of each data frame in the list into a single data frame
  # Note: this step requires equivalent variable names for all data frames
  if(collapse_list){
    print("Combining each model's data into a single data frame for downscaling")
    data <- do.call(bind_rows, data)
  }
  return(data)
} # end function

#' Generate downscaling proxy data for scenarios, countries, iTEM years, and iTEM variable classes
#'
#' @param pop_data_fn file name of data with population by scenario, country, year (including future iTEM years)
#' @param gdp_data_fn file name of data with GDP by scenario, country, year (including future iTEM years)
#' @param co2_data_t0_fn file name of data with CO2 emissions by country, for a base year
#' @param transportenergy_data_t0_fn file name of data with transportation energy consumption data by country,
#' for a base year. May include mode-level detail.
#' @param use_modal_detail logical indicating whether to determine mode-specific proxy values. If false,
#' a single proxy will be calculated for the whole transportation sector.
#' @param apply_modal_elasticities logical indicating whether to differentiate income elasticities by mode.
#' If true, exogenous assumptions are used. If false, all modes are assigned an income elasticity of 1.
#' @param save_output indicate whether to save the output of this function
#' @param create_dir indicate whether to create a new directory if the specified one does not already exist
#' @param output_dir file path where output of this function is saved
#' @details Derives country-level downscaling proxy data for all iTEM years. Does not apply or determine
#' model-specific growth elasticities.
#' @importFrom assertthat assert_that
#' @importFrom tidyr gather
#' @importFrom dplyr bind_rows mutate group_by filter select matches rename full_join left_join if_else
#' @importFrom magrittr "%>%"
generate_ds_proxy_data <- function(pop_data_fn = "downscale/SSP_Population.csv",
                                   gdp_data_fn = "downscale/SSP_GDP_PPP.csv",
                                   co2_data_t0_fn = "downscale/CDIAC_CO2_ctry.csv",
                                   transportenergy_data_t0_fn = "downscale/IEA_trn_ctry.csv",
                                   use_modal_detail = TRUE,
                                   apply_modal_elasticities = TRUE,
                                   save_output = TRUE, create_dir = FALSE,
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
    # Create the directory if called for
    if( create_dir){
      dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
    }
    for(proxy_table in names(proxy_list)){
      write_csv(proxy_list[[proxy_table]],
                path = paste0(output_dir, "/",names(proxy_list[proxy_table]), ".csv"))
    }
  }
  return(proxy_list)
}

#' Generate base-year transportation dataset from which to construct the downscaling proxy
#'
#' @param datafile data table with transportation energy consumption
#' @param mode_mapping_file mapping from mode in the transportation energy data to the iTEM modes
#' @details Derives country-level transportation energy consumption in the base-year by iTEM mode that will
#' be used for constructing the downscaling proxy dataset for transportation-related variables
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

#' Assign country-level socioeconomic scenario to each model/scenario
#'
#' @param data_list list of data tables wherein each element is a model-specific dataframe
#' @param method select a method for assigning scenarios.
#' SSE: minimize sum of squared errors.
#' exogenous: use a default socioeconomic scenario for downscaling all models and scenarios. can be
#' over-ridden for specific model x scenario in exogenous mapping files.
#' @param variable variable to use in determining the assignments; can be population or gdp
#' @details Returns a list of dataframes where each model is an element. Data frames assign model's scenarios
#' to a country-level socioeconomics file.
#' @importFrom assertthat assert_that
#' @importFrom yaml yaml.load_file
#' @importFrom dplyr full_join group_by summarise select mutate rename ungroup filter left_join slice
#' @importFrom magrittr "%>%"
#' @importFrom data.table rbindlist
assign_socioeconomic_scenario <- function( data_list,
                                           method = "exogenous",
                                           SSE_variable = "PPP-GDP"){
  assert_that(is.list(data_list))
  assert_that(method %in% c("exogenous", "SSE"))
  assert_that(SSE_variable %in% c("PPP-GDP", "Population"))

  output_list <- list()
  if(SSE_variable == "PPP-GDP") country_data <- generate_ds_proxy_data()$ds_proxy_gdp
  if(SSE_variable == "Population") country_data <- generate_ds_proxy_data()$ds_proxy_population
  if(method == "exogenous") print("Using exogenous assignments from model/scenario to country-level socio scenario")
  for(model_name in names(data_list)){
    if(method == "exogenous"){
      scenario_assignment <- load_data_file(paste0("model/",model_name,"/scenarios.yaml"), quiet = TRUE) %>%
        rbindlist(idcol = "scenario") %>%
        select(scenario, socio)
      } # end if(method == "exogenous")
    if(method == "SSE"){
      print(paste0("determining country-level socioeconomic scenarios for model: ", model_name))
      # Load the country-to-region assignments for the given model
      region_assignment <- load_data_file(paste0("model/",model_name,"/regions.yaml"), quiet = TRUE)
      # strip any meta-info other than the country names
      region_assignment <- lapply(region_assignment, function(x){x <- x['countries']}) %>%
        rbindlist(idcol = "region") %>%
        rename(iso = countries)
      # Need to figure out if the model provided socioeconomic information. If not, the data frame can be written here
      if(!SSE_variable %in% unique( data_list[[model_name]]$variable)){
        scenario_assignment <- data.frame(scenario = unique(data_list[[model_name]]$scenario),
                                          socio = DS_DEFAULT_SCENARIO)
      } else {
        model_data <- subset( data_list[[model_name]], variable == SSE_variable) %>%
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
                                          socio = SSE_data$scenario_socio)
      } #end else; if(!SSE_variable %in% unique( data_list[[model_name]]$variable))
    } # end if(method == "SSE")
    output_list[[model_name]] <- scenario_assignment
  } # end for(model_name in names(data_list))
  return(output_list)
} # end function



