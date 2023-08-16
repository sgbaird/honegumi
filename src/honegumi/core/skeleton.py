"""
This module contains Honegumi's core functionality.

This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = core.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Functions:
    get_rendered_template_stem(data, option_names):
        Returns a string that represents the rendered template stem based on the
        given data and option names.
    unpack_rendered_template_stem(rendered_template_stem):
        Extracts option values from a rendered template stem string.
    fib(n):
        Fibonacci example function that returns the n-th Fibonacci number.
    parse_args(args):
        Parses command line parameters.
    setup_logging(loglevel):
        Sets up basic logging.
    main(args):
        Wrapper allowing fib to be called with string arguments in a CLI fashion.
    run():
        Calls main passing the CLI arguments extracted from sys.argv.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys
import time
from typing import List

import _pytest
import pytest

from honegumi.core import __version__

# from jinja2 import Environment, FileSystemLoader

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from honegumi.core.skeleton import fib`,
# when using this Python module as a library.


def get_rendered_template_stem(datum, option_names):
    """
    Returns a string that represents the rendered template stem based on the given data
    and option names.

    Parameters
    ----------
    data : dict
        A dictionary containing the data to be used in the rendered template stem.
    option_names : list
        A list of strings representing the names of the options to be included in the
        rendered template stem.

    Returns
    -------
    str
        A string representing the rendered template stem.

    Examples
    --------
    >>> data = {'option1': 'value1', 'option2': 'value2'}
    >>> option_names = ['option1', 'option2']
    >>> get_rendered_template_stem(data, option_names)
    'option1-value1__option2-value2'
    """
    rendered_template_stem = "__".join(
        [f"{option_name}-{str(datum[option_name])}" for option_name in option_names]
    )  # `str()` was intended for boolean values, but no longer using booleans
    return rendered_template_stem


def unpack_rendered_template_stem(rendered_template_stem):
    """
    This function takes a rendered template stem as input and returns a dictionary of
    options and their values.

    Parameters
    ----------
    rendered_template_stem : str
        The rendered template stem to be unpacked.

    Returns
    -------
    dict
        A dictionary containing the options and their values.

    Examples
    --------
    >>> unpack_rendered_template_stem("option1-value1__option2-value2__option3-value3")
    {'option1': 'value1', 'option2': 'value2', 'option3': 'value3'}
    """
    options = {}

    # split the string into a list of option-value pairs
    option_value_pairs = rendered_template_stem.split("__")

    # extract the option names and values from the pairs and add them to a dictionary
    for pair in option_value_pairs:
        option_name, option_value = pair.split("-")

        if option_value.lower() == "true":
            option_value = True
        elif option_value.lower() == "false":
            option_value = False
        elif option_value.isdigit():
            option_value = int(option_value)
        elif option_value.replace(".", "", 1).isdigit():
            option_value = float(option_value)

        options[option_name] = option_value

    return options


class ResultsCollector:
    """A class for collecting and summarizing results of pytest test runs.

    https://stackoverflow.com/a/72278485/13697228

    Attributes
    ----------
    reports : List[pytest.TestReport]
        A list of test reports generated during the test run.
    collected : int
        The number of test items collected for the test run.
    exitcode : int
        The exit code of the test run.
    passed : List[pytest.TestReport]
        A list of test reports for tests that passed.
    failed : List[pytest.TestReport]
        A list of test reports for tests that failed.
    xfailed : List[pytest.TestReport]
        A list of test reports for tests that were expected to fail but passed.
    skipped : List[pytest.TestReport]
        A list of test reports for tests that were skipped.
    total_duration : float
        The total duration of the test run in seconds.

    Examples
    --------
    >>> collector = ResultsCollector()
    >>> # run pytest tests
    >>> collector.total_duration
    10.123456789
    """

    def __init__(self) -> None:
        self.reports: List[pytest.TestReport] = []
        self.collected: int = 0
        self.exitcode: int = 0
        self.passed: List[pytest.TestReport] = []
        self.failed: List[pytest.TestReport] = []
        self.xfailed: List[pytest.TestReport] = []
        self.skipped: List[pytest.TestReport] = []
        self.total_duration: float = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(
        self, item: pytest.Item, call: pytest.CallInfo
    ) -> None:
        """A pytest hook for collecting test reports.

        Parameters
        ----------
        item : pytest.Item
            The test item being run.
        call : pytest.CallInfo
            The result of running the test item.

        Examples
        --------
        >>> item = ...
        >>> call = ...
        >>> collector = ResultsCollector()
        >>> collector.pytest_runtest_makereport(item, call)
        """

        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items: List[pytest.Item]) -> None:
        """A pytest hook for modifying collected test items.

        Parameters
        ----------
        items : List[pytest.Item]
            A list of pytest.Item objects representing the collected test items.

        Examples
        --------
        >>> items = ...
        >>> collector = ResultsCollector()
        >>> collector.pytest_collection_modifyitems(items)
        """

        self.collected = len(items)

    def pytest_terminal_summary(
        self, terminalreporter: _pytest.terminal.TerminalReporter, exitstatus: int
    ) -> None:
        """A pytest hook for summarizing test results.

        Parameters
        ----------
        terminalreporter : pytest.terminal.TerminalReporter
            The terminal reporter object used to report test results.
        exitstatus : int
            The exit status code of the test run.

        Examples
        --------
        >>> terminalreporter = ...
        >>> exitstatus = ...
        >>> collector = ResultsCollector()
        >>> collector.pytest_terminal_summary(terminalreporter, exitstatus)
        """

        self.exitcode = exitstatus
        self.passed = terminalreporter.stats.get("passed", [])
        self.failed = terminalreporter.stats.get("failed", [])
        self.xfailed = terminalreporter.stats.get("xfailed", [])
        self.skipped = terminalreporter.stats.get("skipped", [])
        self.num_passed = len(self.passed)
        self.num_failed = len(self.failed)
        self.num_xfailed = len(self.xfailed)
        self.num_skipped = len(self.skipped)

        self.total_duration = time.time() - terminalreporter._sessionstarttime


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for _i in range(n - 1):
        a, b = b, a + b
    return a


# # Create an environment with the template directory
# template_dir = "."
# env = Environment(loader=FileSystemLoader(template_dir))

# # Load the template file
# template_name = "randint.py.jinja"
# template = env.get_template(template_name)

# # Define the data to be rendered
# data = {
#     "min_value": 1,
#     "max_value": 10,
# }

# # print the rendered template
# print(template.render(data))


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version=f"honegumi {__version__}",
    )
    parser.add_argument(dest="n", help="n-th Fibonacci number", type=int, metavar="INT")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")
    print(f"The {args.n}-th Fibonacci number is {fib(args.n)}")
    _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m honegumi.core.skeleton 42
    #
    run()


# %% Code Graveyard

# class ResultsCollector:
#     def __init__(self):
#         self.reports = []
#         # self.data = []
#         self.collected = 0
#         self.exitcode = 0
#         self.passed = 0
#         self.failed = 0
#         self.xfailed = 0
#         self.skipped = 0
#         self.total_duration = 0

#     @pytest.hookimpl(hookwrapper=True)
#     def pytest_runtest_makereport(self, item, call):
#         outcome = yield
#         report = outcome.get_result()
#         # report_info = {
#         #     "stderr": report.capstderr,
#         #     "stdout": report.capstdout,
#         #     "caplog": report.caplog,
#         #     "passed": report.passed,
#         #     "duration": report.duration,
#         #     "nodeid": report.nodeid,
#         #     "fspath": report.fspath,
#         # }
#         if report.when == "call":
#             self.reports.append(report)
#             # self.data.append(report_info)

#     def pytest_collection_modifyitems(self, items):
#         self.collected = len(items)

#     def pytest_terminal_summary(self, terminalreporter, exitstatus):
#         print(exitstatus, dir(exitstatus))
#         self.exitcode = exitstatus
#         self.passed = terminalreporter.stats.get("passed", [])
#         self.failed = terminalreporter.stats.get("failed", [])
#         self.xfailed = terminalreporter.stats.get("xfailed", [])
#         self.skipped = terminalreporter.stats.get("skipped", [])
#         self.num_passed = len(self.passed)
#         self.num_failed = len(self.failed)
#         self.num_xfailed = len(self.xfailed)
#         self.num_skipped = len(self.skipped)

#         self.total_duration = time.time() - terminalreporter._sessionstarttime
