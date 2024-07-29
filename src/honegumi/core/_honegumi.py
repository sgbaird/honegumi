"""
This module contains Honegumi's core functionality.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import io
import logging
import os
import sys
import time
from itertools import product
from os import path
from pathlib import Path
from typing import List
from urllib.parse import quote, urljoin

import _pytest
import jupytext
import pytest
from black import FileMode, format_file_contents

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


def prep_datum_for_render(option_names, datum, is_incompatible_fn=None):
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

    datum[cst.IS_COMPATIBLE_KEY] = not is_incompatible_fn(datum)

    # NOTE: Decided to always keep dummy key false for scripts, let dummy only
    # affect tests
    datum[cst.DUMMY_KEY] = False


def create_notebook(datum, gen_script_path, script, cst=cst):
    github_username = "sgbaird"
    github_prefix = f"https://github.com/{github_username}/honegumi/tree/main/"
    github_link = urljoin(github_prefix, gen_script_path)

    github_badge = f'<a href="{github_link}"><img alt="Open in GitHub" src="https://img.shields.io/badge/Open%20in%20GitHub-blue?logo=github&labelColor=grey"></a>'  # noqa E501

    colab_prefix = (
        "https://colab.research.google.com/github/sgbaird/honegumi/blob/main/"
    )

    notebook_fname = f"{datum['stem']}.ipynb"
    notebook_path = path.join(cst.GEN_NOTEBOOK_DIR, notebook_fname)
    # HACK: issue with + encoding becoming %20 instead of %2B due to use of \\,
    # and maybe other issues (hence both quote fn and replace line)
    encoded_notebook_fname = quote(notebook_fname)
    encoded_notebook_path = path.join(cst.GEN_NOTEBOOK_DIR, encoded_notebook_fname)
    colab_link = urljoin(colab_prefix, encoded_notebook_path).replace("\\", "/")
    colab_badge = f'<a href="{colab_link}"><img alt="Open In Colab" src="https://colab.research.google.com/assets/colab-badge.svg"></a>'  # noqa E501

    preamble = f"{colab_badge} {github_badge}"
    datum[cst.PREAMBLE_KEY] = preamble  # for the HTML template

    # create an intermediate file object for gen_script and prepend colab link
    nb_text = f"# %% [markdown]\n{colab_badge}\n\n# %%\n%pip install ax-platform\n\n# %%\n{script}"  # noqa E501
    gen_script_file = io.StringIO(nb_text)

    # generate the notebook
    notebook = jupytext.read(gen_script_file, fmt="py:percent")

    with open(notebook_path, "w") as f:
        jupytext.write(notebook, f, fmt="notebook")

    return notebook, notebook_path


def generate_script(jinja_var_names, datum, script_template):
    render_datum = {var_name: datum[var_name] for var_name in jinja_var_names}
    script = script_template.render(render_datum)

    # apply black formatting
    script = format_file_contents(script, fast=False, mode=FileMode())

    return script, render_datum


def generate_test(
    script_template, render_datum, dummy=True, render_datum_override_fn=None, cst=cst
):
    test_render_datum = render_datum.copy()
    test_render_datum[cst.DUMMY_KEY] = dummy

    if render_datum_override_fn is not None:
        test_render_datum = render_datum_override_fn(test_render_datum)

    test_script = script_template.render(test_render_datum)
    test_script = format_file_contents(test_script, fast=False, mode=FileMode())

    # indent each line by 4 spaces and prefix def test_script():
    four_spaces = "    "
    rendered_test_template = "def test_script():\n" + "\n".join(
        [four_spaces + line for line in test_script.split("\n")]
    )

    # append the if __name__ == "__main__": block
    rendered_test_template += "\n\nif __name__ == '__main__':\n    test_script()"

    return rendered_test_template


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


# %% Code Graveyard
