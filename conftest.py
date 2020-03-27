import pytest


def pytest_addoption(parser):
    """Add command-line flags for pytest."""
    parser.addoption('--run-slow', action='store_true', help='Run slow tests')


def pytest_runtest_setup(item):
    if 'slow' in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("Give --run-slow to run slow tests")
