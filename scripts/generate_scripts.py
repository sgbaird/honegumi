from itertools import product
from os import path
from pathlib import Path

from ax.modelbridge.factory import Models
from black import FileMode, format_file_contents
from jinja2 import Environment, FileSystemLoader

from honegumi.ax.utils.constants import (
    gen_template_dir,
    model_opt_name,
    objective_opt_name,
    template_dir,
    use_custom_gen_opt_name,
)

env = Environment(loader=FileSystemLoader(template_dir))

# opts stands for options
allowable_opts = {
    objective_opt_name: ["single", "multi"],
    model_opt_name: [Models.GPEI.name, Models.FULLYBAYESIAN.name],
    use_custom_gen_opt_name: [True, False],
}
option_names = list(allowable_opts.keys())
# create all combinations of objective_opts and model_opts while retaining keys
# make it scalable to more option combinations
all_opts = [dict(zip(allowable_opts, v)) for v in product(*allowable_opts.values())]

# remove cases where use_custom_gen_opt_name is False and model_opt_name is
# FULLYBAYESIAN
all_opts = [
    opt
    for opt in all_opts
    if not (
        opt[use_custom_gen_opt_name] is False
        and opt[model_opt_name] == Models.FULLYBAYESIAN.name
    )
]

# create the directory if it doesn't exist
Path(gen_template_dir).mkdir(parents=True, exist_ok=True)


for data in all_opts:
    template_name = "main.py.jinja"
    template = env.get_template(template_name)

    # save the rendered template
    rendered_template_stem = (
        "__".join(
            [f"{option_name}-{str(data[option_name])}" for option_name in option_names]
        )
        + "_test"
    )  # add a test suffix for pytest recognition
    gen_template_name = path.join(gen_template_dir, f"{rendered_template_stem}.py")
    with open(gen_template_name, "w") as f:
        rendered_template = template.render(data)
        # apply black formatting
        rendered_template = format_file_contents(
            rendered_template, fast=False, mode=FileMode()
        )
        f.write(rendered_template)
    1 + 1

# # %% Code Graveyard

# # import importlib
# # "imp0rt": importlib.import_module,
# # https://stackoverflow.com/a/48270196/13697228


# # from honegumi.core.utils.constants import objective_opt_name, model_opt_name

# data = {
#     objective_opt_name: objective,
#     model_opt_name: model,
#     # "imp0rt": importlib.import_module,
#     # https://stackoverflow.com/a/48270196/13697228
# }
