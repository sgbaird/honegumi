from itertools import product
from os import path
from pathlib import Path

import pandas as pd
import pytest
from black import FileMode, format_file_contents
from jinja2 import Environment, FileSystemLoader

from honegumi.ax.utils.constants import (
    doc_dir,
    gen_template_dir,
    model_opt_name,
    objective_opt_name,
    template_dir,
    test_template_dir,
    use_custom_gen_opt_name,
)
from honegumi.core.skeleton import (
    ResultsCollector,
    get_rendered_template_stem,
    unpack_rendered_template_stem,
)

# from ax.modelbridge.factory import Models # causes an issue with pytest!
# i.e., hard-code the model names instead of accessing them programatically
# see https://github.com/facebook/Ax/issues/1781


# import logging
# _logger = logging.getLogger(__name__)

rendered_key = "rendered_template"
is_compatible_key = "is_compatible"

env = Environment(loader=FileSystemLoader(template_dir))

# opts stands for options
option_rows = [
    {"name": objective_opt_name, "options": ["single", "multi"]},
    {"name": model_opt_name, "options": ["GPEI", "FULLYBAYESIAN"]},
    {"name": use_custom_gen_opt_name, "options": [True, False]},
]

# E.g.,
# {
#     "objective": ["single", "multi"],
#     "model": ["GPEI", "FULLYBAYESIAN"],
#     "use_custom_gen": ["Yes", "No"],
# }

option_names = [row["name"] for row in option_rows]

# create all combinations of objective_opts and model_opts while retaining keys
# make it scalable to more option combinations
all_opts = [
    dict(zip(option_names, v))
    for v in product(*[row["options"] for row in option_rows])
]
# E.g.,
# [
#     {"objective": "single", "model": "GPEI", "use_custom_gen": True},
#     {"objective": "single", "model": "GPEI", "use_custom_gen": False},
#     {"objective": "single", "model": "FULLYBAYESIAN", "use_custom_gen": True},
#     {"objective": "single", "model": "FULLYBAYESIAN", "use_custom_gen": False},
#     {"objective": "multi", "model": "GPEI", "use_custom_gen": True},
#     {"objective": "multi", "model": "GPEI", "use_custom_gen": False},
#     {"objective": "multi", "model": "FULLYBAYESIAN", "use_custom_gen": True},
#     {"objective": "multi", "model": "FULLYBAYESIAN", "use_custom_gen": False},
# ]

# remove cases where use_custom_gen_opt_name is False and model_opt_name is
# FULLYBAYESIAN
# all_opts = [
#     opt
#     for opt in all_opts
#     if not (
#         opt[use_custom_gen_opt_name] is False
#         and opt[model_opt_name] == Models.FULLYBAYESIAN.name
#     )
# ]

# track cases where use_custom_gen_opt_name is False and model_opt_name is FULLYBAYESIAN
incompatible_configs = [
    opt
    for opt in all_opts
    if opt[use_custom_gen_opt_name] is False and opt[model_opt_name] == "FULLYBAYESIAN"
]

# create the directory if it doesn't exist
Path(gen_template_dir).mkdir(parents=True, exist_ok=True)
Path(test_template_dir).mkdir(parents=True, exist_ok=True)

# lookup = {} # could probably be a list of dicts instead, but
data = all_opts.copy()

for datum in data:
    # save the rendered template
    rendered_template_stem = get_rendered_template_stem(datum, option_names)

    datum["stem"] = rendered_template_stem

    if datum in incompatible_configs:
        datum[is_compatible_key] = False
        datum[
            rendered_key
        ] = "INVALID: Models.FULLYBAYESIAN requires a custom generation strategy"
        continue

    datum[is_compatible_key] = True

    template_name = "main.py.jinja"
    template = env.get_template(template_name)

    gen_template_name = f"{rendered_template_stem}.py"
    gen_template_path = path.join(gen_template_dir, gen_template_name)

    render_datum = {option_name: datum[option_name] for option_name in option_names}
    rendered_template = template.render(render_datum)
    # apply black formatting
    rendered_template = format_file_contents(
        rendered_template, fast=False, mode=FileMode()
    )

    # rendered_templates[rendered_template_stem] = rendered_template
    datum[rendered_key] = rendered_template

    with open(gen_template_path, "w") as f:
        f.write(rendered_template)

    # indent each line by 4 spaces and prefix def test_script():
    four_spaces = "    "
    rendered_test_template = "def test_script():\n" + "\n".join(
        [four_spaces + line for line in rendered_template.split("\n")]
    )

    # save in tests directory with test_ prefix
    test_template_path = path.join(test_template_dir, f"test_{gen_template_name}")
    with open(test_template_path, "w") as f:
        f.write(rendered_test_template)


collector = ResultsCollector()
# run pytest on one of the test scripts
# (i.e., just the last one assigned to test_template_path)
retcode = pytest.main(["-v", test_template_path], plugins=[collector])
# retcode = pytest.main(["-v", "tests/test_skeleton.py"], plugins=[collector])
for report in collector.reports:
    print("id:", report.nodeid, "outcome:", report.outcome)  # etc
print("exit code:", collector.exitcode)
print(
    "passed:",
    collector.num_passed,
    "failed:",
    collector.num_failed,
    "xfailed:",
    collector.num_xfailed,
    "skipped:",
    collector.num_skipped,
)
print("total duration:", collector.total_duration)

report_data = []

for report in collector.reports:
    # grab the needed info from the report
    report_info = {
        "stderr": report.capstderr,
        "stdout": report.capstdout,
        "caplog": report.caplog,
        "passed": report.passed,
        "duration": report.duration,
        "nodeid": report.nodeid,
        "fspath": report.fspath,
    }

    # extract the stem and remove the `_test` prefix
    stem = Path(report.fspath).stem
    assert stem.startswith("test_"), f"stem {stem} does not start with `test_`"
    stem = stem[5:]

    # unpack the stem into a dictionary
    unpacked_stem = unpack_rendered_template_stem(stem)
    report_datum = {**unpacked_stem, **report_info}
    report_data.append(report_datum)

    # # find the match between report_datum and data
    # match = next(
    #     datum for datum in data if datum[rendered_key] == report_datum[rendered_key]
    # )

report_df = pd.DataFrame(report_data)
data_df = pd.DataFrame(data)

# concatenate the two dataframes to merge the columns based on option_names
# (i.e., the keys)
# merged_df = pd.concat(
#     [data_df, report_df], axis=0, keys=option_names, ignore_index=True
# )
# merged_df = data_df.merge(report_df, on=option_names)
# merged_df = data_df.merge(report_df, how="outer")
# data_df.join(report_df, on=option_names, how="outer")
merged_df = pd.merge(data_df, report_df, on=option_names, how="outer")

# failed_configs = merged_df[merged_df["passed"] == False].to_dict(orient="records")

# find the configs that either failed or were incompatible

invalid_configs = merged_df[
    (merged_df["passed"] == False) | (merged_df[is_compatible_key] == False)  # noqa
][option_names].to_dict(orient="records")

# extract the values for each option name
invalid_configs = [
    [str(opt[option_name]) for option_name in option_names] for opt in invalid_configs
]

# NOTE: `use_custom_gen_opt_name` gets converted to a string from a boolean to
# simply things on a Python/Jinja/Javascript side (i.e., strings are strings,
# but boolean syntax can vary).

# lookup keys should be a string
lookup = {
    ",".join([str(opt[option_name]) for option_name in option_names]): opt[rendered_key]
    for opt in merged_df.to_dict(orient="records")
}

# pytest.main(["-v", test_template_dir])

# Define the path to your HTML template file
core_template_dir = path.join("src", "honegumi", "core")
template_path = "honegumi.html.jinja"

# # Define your variables
# option_rows = [
#     {"name": "row1", "options": ["A", "B"]},
#     {"name": "row2", "options": ["C", "D", "E"]},
#     {"name": "row3", "options": ["F", "G"]},
# ]
# "name" "options" construct might be a bit cleaner than directly as a dictionary
# see main.html.jinja

# lookup = {
#     "A,C,F": "ACF",
#     "A,C,G": "INVALID",
#     "A,D,F": "ADF",
#     "A,D,G": "ADG",
#     "A,E,F": "AEF",
#     "A,E,G": "AEG",
#     "B,C,F": "BCF",
#     "B,C,G": "BCG",
#     "B,D,F": "INVALID",
#     "B,D,G": "BDG",
#     "B,E,F": "INVALID",
#     "B,E,G": "BEG",
# }

# incompatible_configs = [["B", "D", "F"], ["B", "E", "F"], ["A", "C", "G"]]


# Create a Jinja2 environment and load the template file
env = Environment(loader=FileSystemLoader(core_template_dir))
template = env.get_template(template_path)

# Render the template with your variables
html = template.render(
    option_rows=option_rows, lookup=lookup, invalid_configs=invalid_configs
)

# Write the rendered HTML to a file
with open(path.join(doc_dir, "honegumi.html"), "w") as f:
    f.write(html)


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


# option_names = list(option_rows.keys())
# all_opts = [dict(zip(option_rows, v)) for v in product(*option_rows.values())]

# # write data to json file
# with open(path.join("data", "processed", "data.json"), "w") as f:
#     json.dump(all_opts, f, indent=4)

# # write rendered_templates to json file
# with open(path.join("data", "processed", "rendered_templates.json"), "w") as f:
#     json.dump(rendered_templates, f, indent=4)

# {"name": model_opt_name, "options": [Models.GPEI.name, Models.FULLYBAYESIAN.name]},

# invalid_configs = [
#     opt
#     for opt in all_opts
#     if opt[use_custom_gen_opt_name] is False
#     and opt[model_opt_name] == Models.FULLYBAYESIAN.name
# ]


# reports = collector.reports

# print(report.capstderr)
# print(report.capstdout)


# report.fspath

# if (
#     datum[use_custom_gen_opt_name] is False
#     and datum[model_opt_name] == "FULLYBAYESIAN"
# ):
