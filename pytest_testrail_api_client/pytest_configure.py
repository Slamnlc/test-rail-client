import pytest


def pytest_configure():
    pytest.test_results = dict()


def pytest_bdd_after_scenario(request, feature, scenario):
    1 == 1


def pytest_addoption(parser):
    group = parser.getgroup("pytest-rail")