# import pytest


# def pytest_sessionstart(session):
#     session.results = dict()


# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     outcome = yield
#     result = outcome.get_result()

#     if result.when == "call":
#         item.session.results[item] = result
