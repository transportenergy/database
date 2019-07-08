library(testthat)
context("Model database")

item1_rows <- 928541

test_data <- Sys.getenv('ITEM_TEST_DATA')

if (!R.utils::isAbsolutePath(test_data)) {
  test_data <- normalizePath(file.path(getOption('item wd'), test_data))
}

test_paths <- list(`model database`=test_data)

test_that("iTEM1 database has expected # of rows", {
  skip_on_cran()
  skip_on_ci()

  init_paths(test_paths)

  expect_equal(nrow(load_model_data(1)), item1_rows)
})
