from os import path

import pandas as pd

import honegumi.ax.utils.constants as cst
import honegumi.core.utils.constants as core_cst
from honegumi.ax._ax import (
    add_model_specific_keys,
    is_incompatible,
    model_kwargs_test_override,
    option_rows,
    tooltips,
)
from honegumi.core._honegumi import (
    Honegumi,
    create_and_clear_dir,
    create_notebook,
    gen_combs_with_keys,
    generate_lookup_dict,
    get_rendered_template_stem,
)

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
    selections[core_cst.RENDERED_KEY] = script

    if hg.is_incompatible_fn(selections):
        # newline for "INVALID" message formatting
        selections[core_cst.PREAMBLE_KEY] = "\n"
    else:
        selections[core_cst.PREAMBLE_KEY] = ""

    selections["stem"] = get_rendered_template_stem(selections, hg.visible_option_names)

    gen_script_name = f"{selections['stem']}.py"
    gen_script_path = path.join(cst.GEN_SCRIPT_DIR, gen_script_name)

    # # be mindful of max file component length (255?), regardless of path limits
    # # https://stackoverflow.com/a/61628356/13697228

    if is_incompatible(selections):
        selections["stem"] = get_rendered_template_stem(
            selections, hg.visible_option_names
        )
        gen_script_name = f"{selections['stem']}.py"
        gen_script_path = path.join(hg.cst.GEN_SCRIPT_DIR, gen_script_name)

        # HACK: "stem" key required in `selections` within create_notebook()
        notebook, notebook_path = create_notebook(selections, gen_script_path, script)

    new_data.append(selections)

data_df = pd.DataFrame(new_data)

# find the configs that either failed or were incompatible
invalid_configs = data_df[data_df[core_cst.IS_COMPATIBLE_KEY] == False][  # noqa
    hg.option_names
].to_dict(orient="records")

# extract the values for each option name
invalid_configs = [
    [str(opt[option_name]) for option_name in hg.visible_option_names]
    for opt in invalid_configs
]

script_lookup = generate_lookup_dict(
    data_df, hg.visible_option_names, core_cst.RENDERED_KEY
)
preamble_lookup = generate_lookup_dict(
    data_df, hg.visible_option_names, core_cst.PREAMBLE_KEY
)


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
    script_lookup=script_lookup,
    preamble_lookup=preamble_lookup,
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
