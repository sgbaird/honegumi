"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = ax.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import logging

import honegumi.ax.utils.constants as cst
from honegumi.core import __version__  # noqa: F401

# from jinja2 import Environment, FileSystemLoader

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from honegumi.ax.skeleton import fib`,
# when using this Python module as a library.


def fib(n):
    """Fibonacci example function (not actually used in honegumi, just from
    pyscaffold template)

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


def is_incompatible_ax(opt):
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
    model_is_fully_bayesian = opt[cst.MODEL_OPT_KEY] == cst.FULLYBAYESIAN_KEY
    use_custom_threshold = opt[cst.CUSTOM_THRESHOLD_KEY]
    objective_is_single = opt[cst.OBJECTIVE_OPT_KEY] == "single"

    checks = [
        model_is_fully_bayesian and not use_custom_gen,
        objective_is_single and use_custom_threshold,
        # add new incompatibility checks here
    ]
    return any(checks)


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
        if opt[cst.MODEL_OPT_KEY] == cst.FULLYBAYESIAN_KEY
        else {}
    )  # override later to 16 and 32 later on, but only for test script

    # verify that all variables (hidden and visible) are represented
    assert all(
        [opt.get(option_name, None) is not None for option_name in option_names]
    ), f"option_names {option_names} not in opt {opt}"


def model_kwargs_test_override(render_datum):
    model_kwargs = render_datum[cst.MODEL_KWARGS_KEY]
    if "num_samples" in model_kwargs and "warmup_steps" in model_kwargs:
        model_kwargs["num_samples"] = 16
        model_kwargs["warmup_steps"] = 32
    return render_datum
