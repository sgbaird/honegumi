import io
from itertools import product
from os import path
from pathlib import Path
from urllib.parse import urljoin

import jupytext
import pandas as pd
import pytest
from black import FileMode, format_file_contents
from jinja2 import Environment, FileSystemLoader

from honegumi.ax.utils.constants import (
    core_template_dir,
    doc_dir,
    gen_notebook_dir,
    gen_script_dir,
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

rendered_key = "rendered_template"
is_compatible_key = "is_compatible"
preamble_key = "preamble"

env = Environment(loader=FileSystemLoader(template_dir))
core_env = Environment(loader=FileSystemLoader(core_template_dir))

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
#     "use_custom_gen": [True, False],
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

# track cases where use_custom_gen_opt_name is False and model_opt_name is FULLYBAYESIAN
incompatible_configs = [
    opt
    for opt in all_opts
    if opt[use_custom_gen_opt_name] is False and opt[model_opt_name] == "FULLYBAYESIAN"
]

# create the directory if it doesn't exist
Path(gen_script_dir).mkdir(parents=True, exist_ok=True)
Path(gen_notebook_dir).mkdir(parents=True, exist_ok=True)
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

    script_template_name = "main.py.jinja"
    script_template = env.get_template(script_template_name)

    gen_script_name = f"{rendered_template_stem}.py"
    gen_script_path = path.join(gen_script_dir, gen_script_name)

    render_datum = {option_name: datum[option_name] for option_name in option_names}
    script = script_template.render(render_datum)

    # apply black formatting
    script = format_file_contents(script, fast=False, mode=FileMode())

    # rendered_templates[rendered_template_stem] = rendered_template
    datum[rendered_key] = script

    # store GitHub file link
    github_username = "sgbaird"
    github_prefix = f"https://github.com/{github_username}/honegumi/tree/main/"
    github_link = urljoin(github_prefix, gen_script_path)

    github_badge = f'<img alt="Static Badge" src="https://img.shields.io/badge/Open%20GitHub%20Source-blue?logo=github&labelColor=grey&link=<{github_link}>">'  # noqa E501

    colab_prefix = (
        "https://colab.research.google.com/github/sgbaird/honegumi/blob/main/"
    )

    notebook_path = path.join(gen_notebook_dir, f"{rendered_template_stem}.ipynb")
    colab_link = urljoin(colab_prefix, notebook_path)
    colab_badge = f'<a href="{colab_link}"><img alt="Open In Colab" src="https://colab.research.google.com/assets/colab-badge.svg"></a>'  # noqa E501

    preamble = f"{github_badge} {colab_badge}"

    preamble = (
        preamble.replace("/", "%2F")
        .replace(":", "%3A")
        .replace("+", "%2B")
        .replace("-", "%2D")
        .replace("_", "%5F")
        .replace(".", "%2E")
        .replace("!", "%21")
        .replace("~", "%7E")
    )
    # replace "<" with "&lt;" to avoid HTML parsing issues within prism.js
    preamble = preamble.replace("<", "&lt;")

    with open(gen_script_path, "w") as f:
        f.write(script)

    # indent each line by 4 spaces and prefix def test_script():
    four_spaces = "    "
    rendered_test_template = "def test_script():\n" + "\n".join(
        [four_spaces + line for line in script.split("\n")]
    )

    # save in tests directory with test_ prefix
    test_template_path = path.join(test_template_dir, f"test_{gen_script_name}")
    with open(test_template_path, "w") as f:
        f.write(rendered_test_template)

    # create an intermediate file object for gen_script and prepend colab link
    gen_script_file = io.StringIO(script)
    gen_script_file = io.StringIO(
        f"# %% [markdown] \n {colab_badge}\n\n# %%\n{gen_script_file.read()}"
    )
    # print(gen_script_file.getvalue())

    # generate the notebook
    notebook = jupytext.read(gen_script_file, fmt="py:percent")

    with open(notebook_path, "w") as f:
        jupytext.write(notebook, f, fmt="notebook")

    1 + 1


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

report_df = pd.DataFrame(report_data)
data_df = pd.DataFrame(data)

# concatenate the two dataframes to merge the columns based on option_names
# (i.e., the keys)
merged_df = pd.merge(data_df, report_df, on=option_names, how="outer")

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


def generate_lookup_dict(df, option_names, key):
    """
    Generate a lookup dictionary from a pandas DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame(
    >>>     {
    >>>         "option1": ["a", "b", "c"],
    >>>         "option2": [1, 2, 3],
    >>>         "key": ["foo", "bar", "baz"],
    >>>     }
    >>> )
    >>> generate_lookup_dict(df, ['option1', 'option2'], 'key')
    {'a,1': 'foo', 'b,2': 'bar', 'c,3': 'baz'}
    """
    return {
        ",".join([str(opt[option_name]) for option_name in option_names]): opt[key]
        for opt in df.to_dict(orient="records")
    }


lookup = generate_lookup_dict(merged_df, option_names, rendered_key)
preamble = generate_lookup_dict(merged_df, option_names, preamble_key)


# Define the path to your HTML template file
template_path = "honegumi.html.jinja"

# Create a Jinja2 environment and load the template file
script_template = core_env.get_template(template_path)

# Render the template with your variables
html = script_template.render(
    option_rows=option_rows,
    lookup=lookup,
    preamble=preamble,
    invalid_configs=invalid_configs,
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

# merged_df = pd.concat(
#     [data_df, report_df], axis=0, keys=option_names, ignore_index=True
# )
# merged_df = data_df.merge(report_df, on=option_names)
# merged_df = data_df.merge(report_df, how="outer")
# data_df.join(report_df, on=option_names, how="outer")

# failed_configs = merged_df[merged_df["passed"] == False].to_dict(orient="records")

# # find the match between report_datum and data
# match = next(
#     datum for datum in data if datum[rendered_key] == report_datum[rendered_key]
# )

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


# import logging
# _logger = logging.getLogger(__name__)

# pytest.main(["-v", test_template_dir])


# def generate_lookup_dict(df, option_names, key):
#     """
#     Generate a lookup dictionary from a pandas DataFrame.

#     Parameters
#     ----------
#     df : pandas.DataFrame
#         The DataFrame to generate the lookup dictionary from.
#     option_names : list of str
#         The names of the columns to use as options for the lookup dictionary.
#     key : str
#         The name of the column to use as the key for the lookup dictionary.

#     Returns
#     -------
#     dict
#         A lookup dictionary where the keys are comma-separated strings of the
#         option values, and the values are the corresponding values from the
#         key column.

#     Examples
#     --------
#     >>> df = pd.DataFrame({'option1': ['a', 'b', 'c'], 'option2': [1, 2, 3],
#     >>> 'key': ['foo', 'bar', 'baz']}) generate_lookup_dict(df, ['option1',
#     'option2'], 'key') {'a,1': 'foo', 'b,2': 'bar', 'c,3': 'baz'} """ return {
#     ",".join([str(opt[option_name]) for option_name in option_names]):
#     opt[key] for opt in df.to_dict(orient="records") }


# # render notebook
# template_name = "honegumi.ipynb.jinja"
# nb_template = core_env.get_template(template_name)

# title = f"{rendered_template_stem}.py"
# installation = "%pip install ax-platform"

# notebook = nb_template.render(
#     title=title,
#     installation=installation,
#     script=script,
# )

# nb_path = path.join(gen_notebook_dir, f"{rendered_template_stem}.ipynb")

# with open(nb_path, "w") as f:
#     f.write(notebook)

# honegumi.ipynb.jinja
# {
#  "cells": [
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "# {{ title }}"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "{{ installation }}"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "{{ script }}"
#    ]
#   }
#  ],
#  "metadata": {
#   "language_info": {
#    "name": "python"
#   },
#   "orig_nbformat": 4
#  },
#  "nbformat": 4,
#  "nbformat_minor": 2
# }
