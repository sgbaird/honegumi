from os import path

import honegumi.ax.utils.constants as cst
import honegumi.core.utils.constants as core_cst
from honegumi.ax._ax import (
    add_model_specific_keys,
    is_incompatible,
    model_kwargs_test_override,
    option_rows,
    tooltips,
)
from honegumi.core._honegumi import Honegumi, create_and_clear_dir, gen_combs_with_keys

hg = Honegumi(
    cst,
    option_rows=option_rows,
    tooltips=tooltips,
    is_incompatible_fn=is_incompatible,
    add_model_specific_keys_fn=add_model_specific_keys,
    model_kwargs_test_override_fn=model_kwargs_test_override,
)

# removing directories should happen outside of the class
directories = [cst.GEN_SCRIPT_DIR, cst.GEN_NOTEBOOK_DIR, cst.TEST_TEMPLATE_DIR]
[create_and_clear_dir(directory) for directory in directories]

all_opts = gen_combs_with_keys(hg.visible_option_names, hg.visible_option_rows)

data = all_opts.copy()

new_data = []

for selections in data:
    options_model = hg.OptionsModel(**selections)
    script, selections = hg.generate(options_model, return_selections=True)

    # for the HTML template
    selections[core_cst.RENDERED_KEY] = script  # type: ignore

    # "\n" was to complement open in colab badge line
    selections[core_cst.PREAMBLE_KEY] = ""  # type: ignore

    new_data.append(selections)

# Find the configs that either failed or were incompatible
invalid_configs = [
    {key: value for key, value in item.items() if key in hg.option_names}
    for item in new_data
    if not item[core_cst.IS_COMPATIBLE_KEY]
]

# Extract the values for each option name
invalid_configs = [
    [str(opt[option_name]) for option_name in hg.visible_option_names]
    for opt in invalid_configs
]


# Define the path to your HTML template file
template_path = "honegumi.html.jinja"

# Create a Jinja2 environment and load the template file
template = hg.core_env.get_template(template_path)

# convert boolean values within option_rows to strings
for row in hg.jinja_option_rows:
    row["options"] = [str(opt) for opt in row["options"]]

# Render the template with your variables
html = template.render(
    jinja_option_rows=hg.jinja_option_rows,
    invalid_configs=invalid_configs,
)

# Write the rendered HTML to a file
with open(path.join(core_cst.DOC_DIR, "honegumi.html"), "w") as f:
    f.write(html)

# TODO: run make html command from here

1 + 1


# doesn't work on Windows due to https://stackoverflow.com/a/61628356/13697228
# try:
#     with open(gen_script_path, "w") as f:
#         f.write(script)

# except Exception as e:
#     # Get the absolute path of the file
#     abs_gen_script_path = os.path.abspath(gen_script_path)

#     # Add the \\?\ prefix to the absolute path to disable string parsing
#     # by Windows API
#     abs_gen_script_path = "\\\\?\\" + abs_gen_script_path

#     with open(abs_gen_script_path, "w") as f:
#         f.write(script)

# # track cases where certain combinations of non-hidden options are invalid
# incompatible_configs = [opt for opt in all_opts if is_incompatible_ax(opt)]
