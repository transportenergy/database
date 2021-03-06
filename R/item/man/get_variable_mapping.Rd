% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/model-downscale.R
\name{get_variable_mapping}
\alias{get_variable_mapping}
\title{Get internal variable mapping assignments (with option to pull an external file instead)}
\usage{
get_variable_mapping(mapping_fn = "downscale/variable_ds_proxy.csv", ...)
}
\arguments{
\item{mapping_fn}{file path and name of variable mapping}
}
\description{
Get internal variable mapping assignments (with option to pull an external file instead)
}
\details{
Takes in a csv table with variables and associated categories. Defaults to the one provided with the item
package, but can be set to a different one.
}
