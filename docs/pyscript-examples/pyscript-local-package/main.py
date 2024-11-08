# import os

import constants as cst
import js
from js import invalidConfigs, optionRows

from honegumi import Honegumi

# print("importing constants...")
# print(f"Current directory: {os.getcwd()}")
# # ls
# print(f"Files in current directory: {os.listdir()}")


# print("importing honegumi...")


# Create an instance of Honegumi with the appropriate context and options
hg = Honegumi(cst)
# hg = Honegumi(cst, option_rows)

invalid_configs = invalidConfigs
option_rows_temp = optionRows

# Ensure invalid_configs is a list of lists
if isinstance(invalid_configs, str):
    import ast

    invalid_configs = ast.literal_eval(invalid_configs)

option_rows = list(row.to_py() for row in option_rows_temp)


def generate_rendered(kwargs):
    """
    Define the logic to generate the rendered content based on the kwargs.
    """
    return f"Rendered content based on kwargs: {kwargs}"


def generate_preamble(current_config):
    """
    Define the logic to generate the preamble content based on the current
    configuration.
    """
    return f"Preamble content based on current config: {current_config}"


def get_deviating_options(current_config, invalid_configs):
    """
    Get the options that deviate from the current configuration based on the
    invalid configurations.
    """

    # Convert to tuples
    current_config = tuple(current_config)
    invalid_configs = [tuple(config) for config in invalid_configs]

    print(f"Current Config: {current_config}")
    print(f"Invalid Configs: {invalid_configs}")

    # Generate all possible configurations that deviate by exactly one option
    possible_deviating_configs = [
        [option if i == idx else current_config[i] for i in range(len(current_config))]
        for idx, options in enumerate(option_rows)
        for option in options["options"]
        if option != current_config[idx]
    ]

    # Remove duplicate configurations
    possible_deviating_configs = list(
        {tuple(config) for config in possible_deviating_configs}
    )

    # Debug: Print possible deviating configurations
    print("Possible Deviating Configs:", possible_deviating_configs)

    # Find the invalid configurations that match the deviating configurations
    deviating_configs = [
        config for config in possible_deviating_configs if config in invalid_configs
    ]

    # Debug: Print deviating configurations
    print("Deviating Configs:", deviating_configs)

    # Identify the deviating options based on the configurations
    deviating_options = [
        f"{option_rows[idx]['name']}-{config[idx]}"
        for config in deviating_configs
        for idx in range(len(config))
        if config[idx] != current_config[idx]
    ]

    # Check if the current configuration is invalid
    is_invalid = any(config == current_config for config in invalid_configs)

    # If the current configuration is invalid, highlight all selected options
    if is_invalid:
        current_config_with_name = [
            f"{option_rows[i]['name']}-{value}"
            for i, value in enumerate(current_config)
        ]
        deviating_options.extend(current_config_with_name)

    # Debug: Print deviating options
    print("Deviating Options:", deviating_options)

    return deviating_options


def update_text():
    """
    Handle the updating of text and rendering based on the current radio button
    selections. This function also manages invalid configurations and highlights
    deviations.
    """
    rows = js.document.querySelectorAll('input[type="radio"]:checked')
    labels = js.document.querySelectorAll("label")

    # Reset label text for all labels
    for label in labels:
        if label.htmlFor != rows[0].id:
            label.innerHTML = label.textContent

    # Gather the current configuration and kwargs from the selected radio buttons
    current_config = [row.value for row in rows]
    kwargs = {row.name: row.value for row in rows}

    # Generate the rendered code and preamble using the helper functions
    rendered = generate_rendered(kwargs)
    preamble = generate_preamble(current_config)

    # Update the HTML elements with the generated content
    js.document.getElementById("preamble").innerHTML = preamble
    js.document.getElementById("text").innerHTML = f"\n{rendered}"

    deviating_options = get_deviating_options(current_config, invalid_configs)

    # Apply strikethrough formatting to labels of deviating options
    for option in deviating_options:
        label = js.document.querySelector(f'label[for="{option}"]')
        if label:
            label.innerHTML = f"<s>{label.innerHTML}</s>"

    # Re-highlight the code block using Prism.js
    js.Prism.highlightAll()


# initialize the text content
update_text()
