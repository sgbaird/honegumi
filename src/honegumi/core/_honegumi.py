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
from typing import Any, Dict, List, Tuple, Union

import _pytest
import pytest

import honegumi.core.utils.constants as core_cst
from honegumi import __version__
from honegumi.ax._ax import (
    add_model_specific_keys,
    extra_jinja_var_names,
    is_incompatible,
    model_kwargs_test_override,
    option_rows,
)

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


try:
    from pyscript import window

    log_fn = window.console.log
except Exception:

    def log_fn(x):
        return x


# ---- Python API ----


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


def create_options_model(option_rows: List[Dict[str, Any]]):
    fields = {}

    for row in option_rows:
        name = row["name"]
        display_name = row["display_name"]  # noqa: F841
        options = row["options"]
        hidden = row["hidden"]
        disable = row["disable"]

        # Handle different types of options (e.g., bool, str)
        if all(isinstance(opt, bool) for opt in options):
            field_type = bool
        elif all(isinstance(opt, str) for opt in options):
            field_type = str
        else:
            field_type = Any  # Fallback for mixed types

        # Handle field default and other metadata
        default_value = options[0]  # Default to the first option in the list
        fields[name] = (
            field_type,
            Field(
                default=default_value,
                description=name,
                json_schema_extra={"hidden": hidden, "disable": disable},
            ),
        )

        # NOTE: This may be conflicting and causing confusion relative to
        # add_model_specific_keys, since originally I was using e.g.,
        # `opt.setdefault(cst.CUSTOM_GEN_KEY, opt[cst.MODEL_OPT_KEY] ==
        # cst.FULLYBAYESIAN_KEY)`

        # TODO: auto-create the docstring __doc__ since this dynamically
        # generates the pydantic model (i.e., useful hover typehints are lost)
        # https://chatgpt.com/share/d3cce48d-effe-4496-82be-476c1889e7fd

    # Create a Pydantic model dynamically
    model = create_model("OptionsModel", **fields)
    return model


class Honegumi:
    def __init__(
        self,
        cst,
        option_rows: List[Dict[str, Any]] = option_rows,
        script_template_dir=os.path.join("src", "honegumi", "ax"),
        script_template_name="main.py.jinja",
        core_template_dir=os.path.join("src", "honegumi", "core"),
        core_template_name="honegumi.html.jinja",
        output_dir="docs",
        output_name="honegumi.html",
        is_incompatible_fn=is_incompatible,
        add_model_specific_keys_fn=add_model_specific_keys,
        model_kwargs_test_override_fn=model_kwargs_test_override,
        dummy=None,
        skip_tests=None,
    ):
        self.cst = cst

        self.output_dir = output_dir
        self.output_name = output_name

        self.is_incompatible_fn = is_incompatible_fn
        self.add_model_specific_keys_fn = add_model_specific_keys_fn
        self.model_kwargs_test_override_fn = model_kwargs_test_override_fn

        self.option_rows = option_rows

        # Generate the Pydantic options model dynamically
        self.OptionsModel = create_options_model(option_rows)

        if dummy is None:
            dummy = os.getenv("SMOKE_TEST", "False").lower() == "true"

        if skip_tests is None:
            skip_tests = os.getenv("SKIP_TESTS", "False").lower() == "true"

        self.dummy = dummy
        self.skip_tests = skip_tests

        if dummy:
            print("DUMMY RUN / SMOKE TEST FOR FASTER DEBUGGING")

        if skip_tests:
            print("SKIPPING TESTS")

        self.env = Environment(
            loader=FileSystemLoader(script_template_dir),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

        self.template = self.env.get_template(script_template_name)

        self.core_env = Environment(
            loader=FileSystemLoader(core_template_dir),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

        self.core_template = self.core_env.get_template(core_template_name)

        # remove the options where disable is True, and print disabled options (keep
        # track of disabled option names and default values)
        self.disabled_option_defaults = [
            {row["name"]: row["options"][0]} for row in option_rows if row["disable"]
        ]
        disabled_option_names = [row["name"] for row in option_rows if row["disable"]]

        active_option_rows = [row for row in option_rows if not row["disable"]]

        self.active_option_rows = active_option_rows

        # E.g.,
        # {
        #     "objective": ["single", "multi"],
        #     "model": ["GPEI", "FULLYBAYESIAN"],
        #     "use_custom_gen": [True, False],
        # }

        if self.disabled_option_defaults:
            print("The following options have been disabled:")
            for default in self.disabled_option_defaults:
                print(f"Disabled option and default: {default}")

        self.active_option_names = [row["name"] for row in active_option_rows]

        self.visible_option_names = [
            row["name"] for row in active_option_rows if not row["hidden"]
        ]
        self.visible_option_rows = [
            row for row in active_option_rows if not row["hidden"]
        ]

        self.jinja_var_names = (
            self.active_option_names + extra_jinja_var_names + disabled_option_names
        )

        self.jinja_option_rows = [row for row in self.visible_option_rows]

    def process_selections(self, options_model: BaseModel):
        # You can check if selections is an instance of the expected type
        if not isinstance(options_model, self.OptionsModel):
            warnings.warn(f"Expected {self.OptionsModel}, got {type(options_model)}")

        # Convert validated selections to a dict
        selections = options_model.model_dump()

        # set the default values for the disabled options
        for default in self.disabled_option_defaults:
            selections.update(default)

        # in-place operation
        self.add_model_specific_keys_fn(self.active_option_names, selections)

        # NOTE: Decided to always keep dummy key false for scripts (as opposed to tests)
        selections[core_cst.DUMMY_KEY] = False

        selections = {
            var_name: selections[var_name] for var_name in self.jinja_var_names
        }

        selections[core_cst.IS_COMPATIBLE_KEY] = not self.is_incompatible_fn(selections)

        return selections

    def generate(
        self, options_model: BaseModel, return_selections=False
    ) -> Union[str, Tuple[str, Dict[str, Any]]]:

        selections = self.process_selections(options_model)

        if self.is_incompatible_fn(selections):
            # override
            script = "INVALID: The parameters you have selected are incompatible, either from not being implemented or being logically inconsistent."  # noqa E501

        else:
            script = self.template.render(selections)
            # apply black formatting
            script = format_file_contents(script, fast=False, mode=FileMode())

        if return_selections:
            return script, selections

        return script

    def get_deviating_options(self, current_config: dict):
        """
        Get the options that deviate by zero or one elements from the current
        configuration based on the invalid configurations.
        """

        current_config = self.process_selections(self.OptionsModel(**current_config))
        current_is_valid = current_config[core_cst.IS_COMPATIBLE_KEY]
        current_config = {key: current_config[key] for key in self.visible_option_names}

        possible_deviating_configs = []
        for option_row in self.visible_option_rows:
            option_name = option_row["name"]
            for option in option_row["options"]:
                # Only consider options that differ from the current config
                if str(option) != str(current_config[option_name]):
                    new_config = current_config.copy()
                    new_config[option_name] = option
                    model = self.OptionsModel(**new_config)
                    new_config = self.process_selections(model)
                    # log_fn(f"New config: {new_config}")
                    if not new_config[core_cst.IS_COMPATIBLE_KEY]:
                        new_config = {
                            key: new_config[key] for key in self.active_option_names
                        }
                        possible_deviating_configs.append(new_config)

        # https://stackoverflow.com/a/9427216
        # Remove duplicate configurations using flattened tuples
        seen_configs = set()
        unique_configs = []
        for config in possible_deviating_configs:
            # Convert the dictionary to a tuple of key-value pairs, converting nested
            # dictionaries to strings
            config_tuple = tuple(
                (k, str(v) if isinstance(v, dict) else v) for k, v in config.items()
            )
            if config_tuple not in seen_configs:
                seen_configs.add(config_tuple)
                unique_configs.append(config)

        deviating_configs = [dict(config) for config in unique_configs]
        # possible_deviating_configs = [dict(config) for config in unique_configs]

        # # Find the invalid configurations out of the possible ones
        # deviating_configs = [
        #     config
        #     for config in possible_deviating_configs
        #     if self.is_incompatible_fn(config)
        # ]

        # Identify the one option from each "deviates by one" configuration
        deviating_options = []
        for config in deviating_configs:
            for name in self.visible_option_names:
                if config[name] != current_config[name]:
                    deviating_options.append({name: config[name]})

        # If current configuration is invalid, append all options
        if not current_is_valid:
            for name, value in current_config.items():
                deviating_options.append({name: value})

        return deviating_options


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

# NOTE: Still just a placeholder, might be discarded entirely


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

# def get_rendered_template_stem(datum, option_names):
#     """
#     Returns a string that represents the rendered template stem based on the given
#     data
#     and option names.

#     Filenames still have strict character limits even if longpaths enabled on Windows
#     (https://stackoverflow.com/a/61628356/13697228), so use folder structure instead

#     Parameters
#     ----------
#     data : dict
#         A dictionary containing the data to be used in the rendered template stem.
#     option_names : list
#         A list of strings representing the names of the options to be included in the
#         rendered template stem.

#     Returns
#     -------
#     str
#         A string representing the rendered template stem.

#     Examples
#     --------
#     >>> data = {'option1': 'value1', 'option2': 'value2'}
#     >>> option_names = ['option1', 'option2']
#     >>> get_rendered_template_stem(data, option_names)
#     'option1-value1+option2-value2'
#     """
#     rendered_template_stem = "+".join(
#         [f"{option_name}-{str(datum[option_name])}" for option_name in option_names]
#     )  # `str()` was intended for boolean values, but no longer using booleans
#     return rendered_template_stem


# def unpack_rendered_template_stem(rendered_template_stem):
#     """
#     This function takes a rendered template stem as input and returns a dictionary of
#     options and their values.

#     Parameters
#     ----------
#     rendered_template_stem : str
#         The rendered template stem to be unpacked.

#     Returns
#     -------
#     dict
#         A dictionary containing the options and their values.

#     Examples
#     --------
#     >>> unpack_rendered_template_stem("option1-value1+option2-value2+option3-value3")
#     {'option1': 'value1', 'option2': 'value2', 'option3': 'value3'}
#     """
#     options = {}

#     # split the string into a list of option-value pairs
#     option_value_pairs = rendered_template_stem.split("+")

#     # extract the option names and values from the pairs and add them to a dictionary
#     for pair in option_value_pairs:
#         option_name, option_value = pair.split("-")

#         if option_value.lower() == "true":
#             option_value = True
#         elif option_value.lower() == "false":
#             option_value = False
#         elif option_value.isdigit():
#             option_value = int(option_value)
#         elif option_value.replace(".", "", 1).isdigit():
#             option_value = float(option_value)

#         options[option_name] = option_value

#     return options

# # NOTE: `custom_gen_opt_name` gets converted to a string from a boolean to
# # simply things on a Python/Jinja/Javascript side (i.e., strings are strings,
# # but boolean syntax can vary).


# def generate_lookup_dict(data, option_names, key):
#     """
#     Generate a lookup dictionary from a list of dictionaries.

#     Examples
#     --------
#     >>> data = [
#     >>>     {"option1": "a", "option2": 1, "key": "foo"},
#     >>>     {"option1": "b", "option2": 2, "key": "bar"},
#     >>>     {"option1": "c", "option2": 3, "key": "baz"},
#     >>> ]
#     >>> generate_lookup_dict(data, ['option1', 'option2'], 'key')
#     {'a,1': 'foo', 'b,2': 'bar', 'c,3': 'baz'}
#     """
#     if not all(key in item for item in data):
#         raise ValueError(f"key {key} not in all items")
#     return {
#         ",".join([str(item[option_name]) for option_name in option_names]): item[key]
#         for item in data
#     }


# NOTE: `from ax.modelbridge.factory import Models` causes an issue with pytest!
# i.e., hard-code the model names instead of accessing them programatically
# see https://github.com/facebook/Ax/issues/1781

# also, this would make ax an explicit dependency, so perhaps better not to do so.

# if len(current_config) != len(option_rows):
#     raise ValueError(
#         "The length of the current configuration does not match the number of option
#         rows."
#     )
