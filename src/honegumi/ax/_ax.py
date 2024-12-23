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
import honegumi.core.utils.constants  # noqa: F401
from honegumi import __version__  # noqa: F401

# from jinja2 import Environment, FileSystemLoader

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

try:
    from pyscript import window

    log_fn = window.console.log
except Exception:
    log_fn = lambda x: x

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from honegumi.ax.skeleton import fib`,
# when using this Python module as a library.


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
    model_is_fully_bayesian = opt[cst.MODEL_OPT_KEY] == cst.FULLYBAYESIAN_KEY
    # use_custom_threshold = opt.get(cst.CUSTOM_THRESHOLD_KEY, False)
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
    # opt.setdefault(cst.CUSTOM_GEN_KEY, opt[cst.MODEL_OPT_KEY] == cst.FULLYBAYESIAN_KEY)
    # NOTE: setdefault was conflicting with create_model_options, which already was setting defaults
    # Now it's simply overriding whatever was there
    opt[cst.CUSTOM_GEN_KEY] = opt[cst.MODEL_OPT_KEY] == cst.FULLYBAYESIAN_KEY

    # log_fn(f"opt: {opt}")

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
    """make sure tests run faster for SAASBO"""
    model_kwargs = render_datum[cst.MODEL_KWARGS_KEY]
    if "num_samples" in model_kwargs and "warmup_steps" in model_kwargs:
        model_kwargs["num_samples"] = 16
        model_kwargs["warmup_steps"] = 32
    return render_datum


# NOTE: Moved to
# # NOTE: 'model' tooltip can use some clarification once
# # https://github.com/facebook/Ax/issues/2411 is resolved
# tooltips = json.load(open("scripts/resources/tooltips.json"))


# opts stands for options
# TODO: make names more accessible and include tooltip text with details
# REVIEW: consider using only high-level features, not platform-specific details
# NOTE: Hidden variables are ones that I might want to unhide later
option_rows = [
    {
        "name": cst.OBJECTIVE_OPT_KEY,
        "options": ["single", "multi"],
        "hidden": False,
        "disable": False,
        "tooltip": "Choose between <a href='curriculum/concepts/sobo-vs-mobo/sobo-vs-mobo.html'>single and multi-objective optimization</a> based on your project needs. Single objective optimization targets one primary goal (e.g. maximize the strength of a material), while multi-objective optimization considers several objectives simultaneously (e.g. maximize the strength of a material while minimizing synthesis cost). Select the option that best aligns with your optimization goals and problem complexity.",  # noqa E501
    },
    {
        "name": cst.MODEL_OPT_KEY,
        "options": [
            "Default",  # e.g., GPEI
            cst.FULLYBAYESIAN_KEY,  # e.g., FULLYBAYESIAN
        ],  # Change to "Default" and "Fully Bayesian" # noqa E501
        "hidden": False,
        "disable": False,
        "tooltip": "Choose between <a href='curriculum/concepts/freq-vs-bayes/freq-vs-bayes.html'>frequentist and fully bayesian</a> implementations of the gaussian process (GP) surrogate model. The frequentist GP model, which is often the default in BO packages, offers efficiency and speed. The fully Bayesian GP models GP parameters as random variables through MCMC estimation, providing a deeper exploration of uncertainty. The fully bayesian treatment has historically provided better closed loop Bayesian optimization performance, but comes at the cost of higher computational demand. Consider your computational resources and the complexity of your optimization task when making your selection. This option asks you to choose between 'Default' and 'FullyBayesian', where, depending on the other options, 'Default' may be Noisy Gaussian Process Expected Improvement (NGPEI), Noisy Expected Hypervolume Improvement (NEHVI), etc.",  # noqa E501
    },
    {
        "name": cst.CUSTOM_GEN_KEY,
        "options": [False, True],
        "hidden": True,
        "disable": False,
    },
    {
        "name": cst.EXISTING_DATA_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": False,
        "tooltip": "Choose whether to fit the surrogate model to previous data before starting the optimization process. Including historical data may give your model a better starting place and potentially speed up convergence. Conversely, excluding existing data means starting the optimization from scratch, which might be preferred in scenarios where historical data could introduce bias or noise into the optimization process. Consider the relevance and reliability of your existing data when making your selection.",  # noqa E501
    },
    # {"name": USE_CONSTRAINTS_NAME, "options": [False, True], "hidden": False},
    # consider collapsing these three constraints into single option # noqa: E501
    {
        "name": cst.SUM_CONSTRAINT_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to apply a sum constraint over two or more optimization variables (e.g. ensuring total allocation remains within available budget). This constraint focusses generated optimization trials on feasible candidates at the cost of flexibility. Consider whether such a constraint reflects the reality of variable interactions when selecting this option.",  # noqa E501
    },
    {
        "name": cst.ORDER_CONSTRAINT_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to implement an order constraint over two or more optimization variables (e.g. ensuring certain tasks precede others). This constraint focusses generated optimization trials on variable combinations that follow a specific order. Excluding the constraint offers flexibility in variable arrangements but may neglect important task sequencing or value inequality considerations. Consider whether such a constraint reflects the reality of variable interactions when selecting this option.",  # noqa E501
    },
    {
        "name": cst.LINEAR_CONSTRAINT_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to implement a linear constraint over two or more optimization variables such that the linear combination of parameter values adheres to an inequality (e.g. 0.2*x_1 + x_2 < 0.1). This constraint focusses generated optimization trials on variable combinations that follow an enforced rule at the cost of flexibility. Consider whether such a constraint reflects the reality of variable interactions when selecting this option.",  # noqa E501
    },
    {
        "name": cst.COMPOSITIONAL_CONSTRAINT_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to include a composition constraint over two or more optimization variables such that their sum does not exceed a specified total (e.g. ensuring the mole fractions of elements in a composition sum to one). This constraint is particularly relevant to fabrication-related tasks where the quantities of components must sum to a total. Consider whether such a constraint reflects the reality of variable interactions when selecting this option.",  # noqa E501
    },
    {
        "name": cst.CATEGORICAL_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to include a categorical variable in the optimization process (e.g. dark or milk chocolate chips in a cookie recipe). Including categorical variables allows choice parameters and their interaction with continuous variables to be optimized. Note that adding categorical variables can create discontinuities in the search space that are difficult to optimize over. Consider the value of adding categorical variables to the optimization task when selecting this option.",  # noqa E501
    },
    {
        "name": cst.CUSTOM_THRESHOLD_KEY,
        "options": [False, True],
        "hidden": False,
        "disable": False,
        "tooltip": "Choose whether to apply custom thresholds to objectives in a multi-objective optimization problem (e.g. a minimum acceptable strength requirement for a material). Setting a threshold on an objective guides the optimization algorithm to prioritize solutions that meet or exceed these criteria. Excluding thresholds enables greater exploration of the design space, but may produce sub-optimal solutions. Consider whether threshold values reflect the reality or expectations of your optimization task when selection this option.",  # noqa E501
    },
    # {"name": NOISE_OPT_NAME, "options": ["zero", "fixed", "variable", "inferred"], "hidden": False}, # noqa E501 # NOTE: AC Microcourses
    # ⭐ {"name": USE_PREDEFINED_CANDIDATES_NAME, "options": [False, True], "hidden": False}, # e.g., black-box constraints # noqa E501  # NOTE: AC Microcourses
    # {"name": USE_FEATURIZATION_NAME, "options": [False, True], "hidden": False}, # predefined candidates must be True # noqa E501 # NOTE: AC Microcourses (probably leave out, and just include as a tutorial with predefined candidates)
    # ⭐ {"name": USE_CONTEXTUAL_NAME, "options": [False, True], "hidden": False}, # noqa E501 # NOTE: AC Microcourses
    {
        "name": cst.FIDELITY_OPT_KEY,
        "options": ["single", "multi"],
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to perform single or multi-fidelity optimization. Single-fidelity optimization uses a single evaluation method for all optimization trials, while multi-fidelity optimization leverages multiple evaluation methods with varying computational costs. Multi-fidelity optimization can be more efficient than single-fidelity optimization, as it uses cheaper evaluations to guide the optimization process. Consider the availability of different fidelity levels, their computational costs when selecting this option, and compatibility with other algorithms when making this choice.",  # noqa E501
    },  # noqa E501 # NOTE: AC Microcourses
    # {"name": TASK_OPT_NAME, "options": ["single", "multi"], "hidden": False}, # noqa E501 # NOTE: AC Microcourses
    # ⭐⭐ {"name": SHOW_METRICS, "options": [False, True], "hidden": False}, # i.e., visualizations and metrics, e.g., optimization trace, Pareto front, HVI vs. cost # noqa E501 # NOTE: AC Microcourses
    {
        "name": cst.SYNCHRONY_OPT_KEY,
        "options": ["single", "batch"],  # TODO: add "asynchronous"
        "hidden": False,
        "disable": True,
        "tooltip": "Choose whether to perform <a href='curriculum/concepts/batch/single-vs-batch.md'>single or batch evaluations</a> for your Bayesian optimization campaign. Single evaluations analyze one candidate solution at a time, offering precise control and adaptability after each trial at the expense of more compute time. Batch evaluations, however, process several solutions in parallel, significantly reducing the number of optimization cycles but potentially diluting the specificity of adjustments. Batch evaluation is helpful in scenarios where it is advantageous to test several solutions simultaneously. Consider the nature of your evaluation tool when selecting between the two options.",  # noqa E501
    },
    # TODO: Single vs. Batch vs. Asynchronous Optimization, e.g., get_next_trial() vs. get_next_trials() # NOTE: AC Microcourses # noqa E501
    # TODO: Consider adding "human-in-the-loop" toggle, or something else related to start/stop or blocking to wait for human input # noqa E501 # NOTE: AC Microcourses
]

extra_jinja_var_names = [cst.MODEL_KWARGS_KEY, honegumi.core.utils.constants.DUMMY_KEY]
