# Model-specific corrections for BP submitted data
correct_bp <- function( x ){
  #BP's GDP is in 2010 dollar year and in millions. Convert to billion 2005 USD and rename the unit
  BP_GDPconv <- 0.000909
  x %>% mutate(value = if_else(variable == 'PPP-GDP' & unit == "billion US$2010/yr",
                               value * BP_GDPconv, value)) %>%
    mutate(unit = sub("billion US$2010/yr", "billion US$2005/yr", unit)) -> x
  return(x)
}
