import js
from js import invalidConfigs, optionRows

# Convert JavaScript variables to Python data structures
option_rows = list(row.to_py() for row in optionRows)
invalid_configs = invalidConfigs.to_py()


def generate_rendered(kwargs):
    """
    Generate the rendered content based on the kwargs using Honegumi.
    """
    # Placeholder for any context-specific data you may need
    cst = ...

    # Importing honegumi and defining the model using the kwargs
    from honegumi import Honegumi

    # Create an instance of Honegumi with the appropriate context and options
    hg = Honegumi(cst, option_rows)
    options_model = hg.OptionsModel(**kwargs)
    result = hg.generate(options_model)
    return result


def generate_preamble(current_config):
    """
    Generate the preamble content based on the current configuration.
    """
    return ""


def update_text(event=None):
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

    # Find the invalid configurations that match the deviating configurations
    deviating_configs = [
        config
        for config in invalid_configs
        if any(deviation == config for deviation in possible_deviating_configs)
    ]

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

    # Apply strikethrough formatting to labels of deviating options
    for option in deviating_options:
        label = js.document.querySelector(f'label[for="{option}"]')
        if label:
            label.innerHTML = f"<s>{label.innerHTML}</s>"

    # Re-highlight the code block using Prism.js
    js.Prism.highlightAll()
