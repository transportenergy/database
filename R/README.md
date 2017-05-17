R tools for the iTEM databases
==============================

Installation
------------

Use [`devtools`](https://cran.r-project.org/package=devtools). From source (for instance, to develop the code locally):

```
$ git clone git@github.com:transportenergy/database.git
$ Rscript -e "devtools::install_local('database/R/item')"
```

Or without cloning the repository:

```r
devtools::install_github('transportenergy/database/R/item')
```

Usage
-----

### From R scripts

``` r
library(item)

data <- item::load_model_data(1)  # Load version 1 of the iTEM models database
```

### Command line

`run` is an executable that invokes `item::cli()`. It can be used without installing the package.

```
$ ./run
Loading item
Usage: ./run [OPTIONS] COMMAND
Command-line interface for the iTEM databases.

…

Commands:
  mkdirs
  debug
  load_model_data
```


Development
-----------

Code conventions and packaging follow the [“R packages” book](http://r-pkgs.had.co.nz/).

`test` is an executable that runs the tests in `./item/tests/testthat`. The environment variable `ITEM_TEST_DATA` must be defined in order for these tests to work:

```
$ export ITEM_TEST_DATA=../../data/model/database
$ ./test
Loading item
Loading required package: testthat
Testing item
Model database: .

DONE ============================================
```
