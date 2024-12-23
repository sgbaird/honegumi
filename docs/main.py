from pyscript import window
import js

# from js import invalidConfigs

# from js import optionRows

import os

from honegumi.core._honegumi import Honegumi

# from honegumi.core._honegumi import Honegumi, get_deviating_options
from honegumi.ax.utils import constants as cst

from honegumi.ax._ax import (
    add_model_specific_keys,
    is_incompatible,
    model_kwargs_test_override,
    option_rows,
)

# invalid_configs = invalidConfigs

# option_rows_temp = optionRows

# use to_py()

# invalid_configs = [config.to_py() for config in invalid_configs]

# # Ensure invalid_configs is a list of lists
# if isinstance(invalid_configs, str):
#     import ast

#     invalid_configs = ast.literal_eval(invalid_configs)

# option_rows = list(row.to_py() for row in option_rows_temp)

# REVIEW: Not sure if below was working properly
# # Convert JavaScript variables to Python data structures
# option_rows = list(row.to_py() for row in optionRows)
# invalid_configs = invalidConfigs.to_py()

# SMOKE_TEST = True

# if SMOKE_TEST:
#     option_names_shortlist = [
#         cst.OBJECTIVE_OPT_KEY,
#         cst.CUSTOM_GEN_KEY,
#         cst.MODEL_OPT_KEY,
#         cst.EXISTING_DATA_KEY,
#         cst.CUSTOM_THRESHOLD_KEY,
#     ]

#     option_rows = [
#         option_row
#         for option_row in option_rows
#         if option_row["name"] in option_names_shortlist
#     ]

hg = Honegumi(
    cst,
    option_rows=option_rows,
    is_incompatible_fn=is_incompatible,
    add_model_specific_keys_fn=add_model_specific_keys,
    model_kwargs_test_override_fn=model_kwargs_test_override,
    script_template_dir=os.path.join("honegumi", "ax"),
    script_template_name="main.py.jinja",
    core_template_dir=os.path.join("honegumi", "core"),
    core_template_name="honegumi.html.jinja",
    output_dir="docs",
    output_name="honegumi.html",
)


def generate_rendered(kwargs):
    """
    Generate the rendered content based on the kwargs using Honegumi.
    """
    # Create an instance of Honegumi with the appropriate context and options
    options_model = hg.OptionsModel(**kwargs)
    result = hg.generate(options_model)
    return result


def generate_preamble(current_config):
    """
    Generate the preamble content based on the current configuration.
    """
    return ""


def update_text(event):
    """
    Handle the updating of text and rendering based on the current radio button
    selections. This function also manages invalid configurations and highlights
    deviations.
    """
    # window.console.log(event)

    rows = js.document.querySelectorAll('input[type="radio"]:checked')
    labels = js.document.querySelectorAll("label")

    # Reset label text for all labels
    for label in labels:
        if label.htmlFor != rows[0].id:
            label.innerHTML = label.textContent

    # Gather the current configuration and kwargs from the selected radio buttons
    current_config = {row.name: row.value for row in rows}
    # window.console.log(f"Current config: {current_config}")

    current_opt_model = hg.OptionsModel(**current_config)
    current_config = hg.process_selections(current_opt_model)

    # window.console.log(f"Current config: {current_config}")

    # window.console.log(f"Invalid configs: {invalid_configs[0].to_py()}")

    # Generate the rendered code and preamble using the helper functions
    rendered = generate_rendered(current_config)
    preamble = generate_preamble(current_config)

    # Update the HTML elements with the generated content
    js.document.getElementById("preamble").innerHTML = preamble
    js.document.getElementById("text").innerHTML = f"\n{rendered}"

    deviating_options = hg.get_deviating_options(current_config)

    # window.console.log(f"Deviating options: {deviating_options}")

    # Apply strikethrough formatting to labels of deviating options
    for name, option in deviating_options.items():
        label = js.document.querySelector(f'label[for="{name}-{option}"]')
        if label:
            label.innerHTML = f"<s>{label.innerHTML}</s>"

    # Re-highlight the code block using Prism.js
    js.Prism.highlightAll()


# initialize the text content
update_text(None)


## % Code Graveyard

# def get_deviating_options(current_config: dict, is_incompatible_fn, option_rows):
#     """
#     Get the options that deviate by zero or one elements from the current
#     configuration based on the invalid configurations.
#     """
#     if len(current_config) != len(option_rows):
#         raise ValueError(
#             "The length of the current configuration does not match the number of option rows."
#         )

#     possible_deviating_configs = []
#     for option_row in option_rows:
#         option_name = option_row["name"]
#         for option in option_row["options"]:
#             # Only consider options that differ from the current config
#             if str(option) != str(current_config[option_name]):
#                 new_config = current_config.copy()
#                 new_config[option_name] = option
#                 possible_deviating_configs.append(new_config)

#     window.console.log(f"Possible deviating configs: {possible_deviating_configs}")

#     # Remove duplicate configurations (preserve order to make debugging easier)
#     # https://stackoverflow.com/a/9427216
#     seen_configs = set()
#     unique_configs = []
#     for config in possible_deviating_configs:
#         config_tuple = tuple(config.items())
#         if config_tuple not in seen_configs:
#             seen_configs.add(config_tuple)
#             unique_configs.append(config)

#     possible_deviating_configs = [dict(config) for config in unique_configs]

#     # Find the invalid configurations out of the possible ones
#     deviating_configs = [
#         config for config in possible_deviating_configs if is_incompatible_fn(config)
#     ]

#     # Identify the one option from each "deviates by one" configuration
#     deviating_options = {}
#     for config in deviating_configs:
#         for name in config:
#             if config[name] != current_config[name]:
#                 deviating_options[name] = config[name]

#     # If current configuration is invalid, highlight all current config options
#     if is_incompatible_fn(current_config):
#         for name, value in current_config.items():
#             deviating_options[name] = value

#     return deviating_options


# # Apply strikethrough formatting to labels of deviating options
# for option in deviating_options:
#     label = js.document.querySelector(f'label[for="{option}"]')
#     if label:
#         label.innerHTML = f"<s>{label.innerHTML}</s>"

# Manually loop through the configurations that deviate by zero or one options from the current configuration, and check to see if they are invalid via hg.is_incompatible()
# This is a workaround for the fact that the get_deviating_options() function does not work properly in the current implementation

# possible_deviating_configs = []
# for option_row in option_rows:
#     option_name = option_row["name"]
#     for option in option_row["options"]:
#         # Only consider options that differ from the current config
#         if option != current_config[option_name]:
#             new_config = current_config.copy()
#             new_config[option_name] = option
#             possible_deviating_configs.append(new_config)

# # Remove duplicate configurations using frozenset
# # https://stackoverflow.com/a/9427216
# unique_configs = {
#     frozenset(config.items()) for config in possible_deviating_configs
# }
# possible_deviating_configs = [dict(config) for config in unique_configs]

# deviating_configs = [
#     config for config in possible_deviating_configs if hg.is_incompatible_fn(config)
# ]
