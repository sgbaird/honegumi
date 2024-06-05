"""
This module contains Honegumi's core functionality.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import os
import sys
import time
from itertools import product
from pathlib import Path
from typing import List

import _pytest
import pytest

import honegumi.ax.utils.constants as cst
from honegumi.core import __version__

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----


def get_rendered_template_stem(datum, option_names):
    """
    Returns a string that represents the rendered template stem based on the given data
    and option names.

    Filenames still have strict character limits even if longpaths enabled on Windows
    (https://stackoverflow.com/a/61628356/13697228), so use folder structure instead

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
    'option1-value1+option2-value2'
    """
    rendered_template_stem = "+".join(
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
    >>> unpack_rendered_template_stem("option1-value1+option2-value2+option3-value3")
    {'option1': 'value1', 'option2': 'value2', 'option3': 'value3'}
    """
    options = {}

    # split the string into a list of option-value pairs
    option_value_pairs = rendered_template_stem.split("+")

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


def create_and_clear_dir(directory):
    # create the directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)

    # clear out the directory (to avoid confusion/running old scripts)
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def gen_combs_with_keys(
    visible_option_names: List[str], visible_option_rows: List[dict]
):
    """
    Generate a list of dictionaries, each representing a combination of options.
    Each dictionary uses option names as keys and the corresponding option from
    each combination as values.

    Parameters
    ----------
    visible_option_names : list of str
        A list of option names. These will be used as the keys in the output
        dictionaries.
    visible_option_rows : list of dict
        A list of dictionaries, each containing an 'options' key associated with
        a list of options. The 'options' from each dictionary are combined to
        form the output dictionaries.

    Returns
    -------
    list of dict
        A list of dictionaries, each representing a combination of options. Each
        dictionary uses option names as keys and the corresponding option from
        each combination as values.

    Examples
    --------
    >>> visible_option_names = ['color', 'size']
    >>> visible_option_rows = [
    ...     {"options": ["red", "blue"]},
    ...     {"options": ["small", "large"]},
    ... ]
    >>> gen_combs_with_keys(visible_option_names, visible_option_rows)
    [
        {"color": "red", "size": "small"},
        {"color": "red", "size": "large"},
        {"color": "blue", "size": "small"},
        {"color": "blue", "size": "large"},
    ]
    """
    all_opts = [
        dict(zip(visible_option_names, v))
        for v in product(*[row["options"] for row in visible_option_rows])
    ]

    return all_opts


# NOTE: `custom_gen_opt_name` gets converted to a string from a boolean to
# simply things on a Python/Jinja/Javascript side (i.e., strings are strings,
# but boolean syntax can vary).


def generate_lookup_dict(df, option_names, key):
    """
    Generate a lookup dictionary from a pandas DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame(
    >>>     {
    >>>         "option1": ["a", "b", "c"],
    >>>         "option2": [1, 2, 3],
    >>>         "key": ["foo", "bar", "baz"],
    >>>     }
    >>> )
    >>> generate_lookup_dict(df, ['option1', 'option2'], 'key')
    {'a,1': 'foo', 'b,2': 'bar', 'c,3': 'baz'}
    """
    if key not in df.columns:
        raise ValueError(f"key {key} not in {df.columns}")
    return {
        ",".join([str(opt[option_name]) for option_name in option_names]): opt[key]
        for opt in df.to_dict(orient="records")
    }


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def fib(n):
    """Fibonacci example function (just to demo CLI usage)

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


def add_model_specific_keys(option_names, opt):
    """Add model-specific keys to the options dictionary (in-place).

    This function adds model-specific keys to the options dictionary `opt`. For
    example, if use_custom_gen is a hidden variable, and the model is
    FULLYBAYESIAN, then use_custom_gen should be True.

    It also sets the value of the key `model_kwargs` based on the value of
    `MODEL_OPT_KEY` in `opt`.

    Parameters
    ----------
    option_names : list
        A list of option names.
    opt : dict
        The options dictionary.

    Examples
    --------
    The following example is demonstrative, the range of cases may be expanded
    later.

    >>> option_names = [
    ...     "objective",
    ...     "model",
    ...     "custom_gen",
    ...     "existing_data",
    ...     "sum_constraint",
    ...     "order_constraint",
    ...     "linear_constraint",
    ...     "composition_constraint",
    ...     "categorical",
    ...     "custom_threshold",
    ...     "fidelity",
    ...     "synchrony",
    ... ]
    >>> opt = {
    ...     "objective": "single",
    ...     "model": "Default",
    ...     "existing_data": False,
    ...     "sum_constraint": False,
    ...     "order_constraint": False,
    ...     "linear_constraint": False,
    ...     "composition_constraint": False,
    ...     "categorical": False,
    ...     "custom_threshold": False,
    ...     "fidelity": "single",
    ...     "synchrony": "single",
    ... }

    >>> add_model_specific_keys(option_names, opt)
    {
        "objective": "single",
        "model": "Default",
        "existing_data": False,
        "sum_constraint": False,
        "order_constraint": False,
        "linear_constraint": False,
        "composition_constraint": False,
        "categorical": False,
        "custom_threshold": False,
        "fidelity": "single",
        "synchrony": "single",
        "custom_gen": False,
        "model_kwargs": {},
    }
    """
    opt.setdefault(cst.CUSTOM_GEN_KEY, opt[cst.MODEL_OPT_KEY] == cst.FULLYBAYESIAN_KEY)

    # increased from the default in Ax tutorials for quality/robustness
    opt["model_kwargs"] = (
        {"num_samples": 1024, "warmup_steps": 1024}
        if opt[cst.MODEL_OPT_KEY] == "FULLYBAYESIAN"
        else {}
    )  # override later to 16 and 32 later on, but only for test script

    # verify that all variables (hidden and visible) are represented
    assert all(
        [opt.get(option_name, None) is not None for option_name in option_names]
    ), f"option_names {option_names} not in opt {opt}"


def is_incompatible(opt):
    """
    Check if the given option dictionary contains incompatible options.

    An option is considered incompatible if it cannot be used together with
    another option. For example, if the model is fully Bayesian, it cannot use
    the custom generator (`use_custom_gen`). Similarly, if the objective is
    single, it cannot use the custom threshold (`use_custom_threshold`).

    Parameters
    ----------
    opt : dict
        The option dictionary to check for incompatibility.

    Returns
    -------
    bool
        True if any incompatibility is found among the options, False otherwise.
    """
    use_custom_gen = opt[cst.CUSTOM_GEN_KEY]
    model_is_fully_bayesian = opt[cst.MODEL_OPT_KEY] == "FULLYBAYESIAN"
    use_custom_threshold = opt[cst.CUSTOM_THRESHOLD_KEY]
    objective_is_single = opt[cst.OBJECTIVE_OPT_KEY] == "single"

    checks = [
        model_is_fully_bayesian and not use_custom_gen,
        objective_is_single and use_custom_threshold,
        # add new incompatibility checks here
    ]
    return any(checks)


def prep_datum_for_render(option_names, datum):
    """
    Checks the compatibility of the given options and updates the datum
    dictionary with the rendered template stem and compatibility status.

    Parameters
    ----------
    option_names : list
        The full list of option names in order to generate the filename stem.
    datum : dict
        The dictionary of option key-value pairs.

    Returns
    -------
    None

    Examples
    --------
    >>> check_compatibility_and_update(['option1', 'option2'], {'option1': 'value1', 'option2': 'value2'}) # noqa: E501
    OUTPUT

    Notes
    -----
    This function will always set the 'dummy' key in the 'datum' dictionary to
    False.
    """
    rendered_template_stem = get_rendered_template_stem(datum, option_names)

    datum["stem"] = rendered_template_stem

    datum[cst.IS_COMPATIBLE_KEY] = not is_incompatible(datum)

    # NOTE: Decided to always keep dummy key false for scripts, let dummy only
    # affect tests
    datum[cst.DUMMY_KEY] = False


# %% Code Graveyard
