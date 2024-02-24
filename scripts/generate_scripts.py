import io
import os
from itertools import product
from os import path
from pathlib import Path
from urllib.parse import urljoin

import jupytext
import pandas as pd
import pytest
from black import FileMode, format_file_contents
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from honegumi.ax.utils.constants import (  # USE_CONSTRAINTS_NAME,
    CATEGORICAL_KEY,
    COMPOSITIONAL_CONSTRAINT_KEY,
    CORE_TEMPLATE_DIR,
    CUSTOM_GEN_KEY,
    CUSTOM_THRESHOLD_KEY,
    DOC_DIR,
    DUMMY_KEY,
    EXISTING_DATA_KEY,
    GEN_NOTEBOOK_DIR,
    GEN_SCRIPT_DIR,
    LINEAR_CONSTRAINT_KEY,
    MODEL_KWARGS_KEY,
    MODEL_OPT_KEY,
    OBJECTIVE_OPT_KEY,
    ORDER_CONSTRAINT_KEY,
    SUM_CONSTRAINT_KEY,
    SYNCHRONY_OPT_KEY,
    TEMPLATE_DIR,
    TEST_TEMPLATE_DIR,
)
from honegumi.core._honegumi import (
    ResultsCollector,
    get_rendered_template_stem,
    unpack_rendered_template_stem,
)

# from ax.modelbridge.factory import Models # causes an issue with pytest!
# i.e., hard-code the model names instead of accessing them programatically
# see https://github.com/facebook/Ax/issues/1781

dummy = os.getenv("SMOKE_TEST", "False").lower() == "true"

if dummy:
    print("DUMMY RUN / SMOKE TEST FOR FASTER DEBUGGING")

rendered_key = "rendered_template"
is_compatible_key = "is_compatible"
preamble_key = "preamble"

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), undefined=StrictUndefined)
core_env = Environment(
    loader=FileSystemLoader(CORE_TEMPLATE_DIR), undefined=StrictUndefined
)

# opts stands for options
# TODO: make names more accessible and include tooltip text with details
# REVIEW: consider using only high-level features, not platform-specific details
# NOTE: Hidden variables are ones that I might want to unhide later
option_rows = [
    {"name": OBJECTIVE_OPT_KEY, "options": ["single", "multi"], "hidden": False},
    {"name": MODEL_OPT_KEY, "options": ["GPEI", "FULLYBAYESIAN"], "hidden": False},
    {"name": CUSTOM_GEN_KEY, "options": [False, True], "hidden": True},
    {"name": EXISTING_DATA_KEY, "options": [False, True], "hidden": False},
    # {"name": USE_CONSTRAINTS_NAME, "options": [False, True], "hidden": False},
    # consider collapsing these three constraints into single option # noqa: E501
    {"name": SUM_CONSTRAINT_KEY, "options": [False, True], "hidden": False},
    {"name": ORDER_CONSTRAINT_KEY, "options": [False, True], "hidden": False},
    {"name": LINEAR_CONSTRAINT_KEY, "options": [False], "hidden": False},
    {
        "name": COMPOSITIONAL_CONSTRAINT_KEY,
        "options": [False, True],
        "hidden": False,
    },  # noqa E501 # NOTE: AC Microcourses
    {"name": CATEGORICAL_KEY, "options": [False, True], "hidden": False},
    {"name": CUSTOM_THRESHOLD_KEY, "options": [False, True], "hidden": False},
    # noise! zero, fixed, variable, inferred
    # {"name": USE_PREDEFINED_CANDIDATES_NAME, "options": [False, True], "hidden": False}, # noqa E501  # NOTE: AC Microcourses
    # {"name": USE_FEATURIZATION_NAME, "options": [False, True], "hidden": False}, # predefined candidates must be True # noqa E501 # NOTE: AC Microcourses
    # {"name": USE_CONTEXTUAL_NAME, "options": [False, True], "hidden": False}, # noqa E501 # NOTE: AC Microcourses
    # {"name": FIDELITY_OPT_NAME, "options": ["single", "multi"], "hidden": False}, # noqa E501 # NOTE: AC Microcourses
    # {"name": TASK_OPT_NAME, "options": [False, True], "hidden": False}, # noqa E501 # NOTE: AC Microcourses
    {
        "name": SYNCHRONY_OPT_KEY,
        "options": ["single", "batch"],  # TODO: add "asynchronous"
        "hidden": False,
    },
    # TODO: Single vs. Batch vs. Asynchronous Optimization, e.g., get_next_trial() vs. get_next_trials() # noqa E501 # NOTE: AC Microcourses
]

# E.g.,
# {
#     "objective": ["single", "multi"],
#     "model": ["GPEI", "FULLYBAYESIAN"],
#     "use_custom_gen": [True, False],
# }

option_names = [row["name"] for row in option_rows]

visible_option_names = [row["name"] for row in option_rows if not row["hidden"]]
visible_option_rows = [row for row in option_rows if not row["hidden"]]

extra_jinja_var_names = [MODEL_KWARGS_KEY, DUMMY_KEY]
jinja_var_names = option_names + extra_jinja_var_names

# create all combinations of objective_opts and model_opts while retaining keys
# make it scalable to more option combinations
all_opts = [
    dict(zip(visible_option_names, v))
    for v in product(*[row["options"] for row in visible_option_rows])
]

for opt in all_opts:
    # If the key-value pair is not already there, then add it based on
    # conditions. For example, if use_custom_gen is a hidden variable, and the
    # model is FULLYBAYESIAN, then use_custom_gen should be True.
    # Do this for each hidden variable.
    opt.setdefault(CUSTOM_GEN_KEY, opt[MODEL_OPT_KEY] == "FULLYBAYESIAN")

    opt["model_kwargs"] = (
        {"num_samples": 256, "warmup_steps": 512}
        if opt[MODEL_OPT_KEY] == "FULLYBAYESIAN"
        else {}
    )  # override later to 16 and 32 later on, but only for test script

    # verify that all variables (hidden and visible) are represented
    assert all(
        [opt.get(option_name, None) is not None for option_name in option_names]
    ), f"option_names {option_names} not in opt {opt}"

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


def is_incompatible(opt):
    """
    Check if the given option is incompatible with other options.

    REVIEW: consider adding a note about why the option is incompatible (could
    get complicated). A compromise would be to indicate whether it's due to not being
    implemented, an API incompatibility, or due to being logically inconsistent.

    Parameters
    ----------
    opt : dict
        The option to check for incompatibility.

    Returns
    -------
    bool
        True if the option is incompatible with other options, False otherwise.
    """
    use_custom_gen = opt[CUSTOM_GEN_KEY]
    model_is_fully_bayesian = opt[MODEL_OPT_KEY] == "FULLYBAYESIAN"
    use_custom_threshold = opt[CUSTOM_THRESHOLD_KEY]
    objective_is_single = opt[OBJECTIVE_OPT_KEY] == "single"

    checks = [
        model_is_fully_bayesian and not use_custom_gen,
        objective_is_single and use_custom_threshold,
        # add new incompatibility checks here
    ]
    return any(checks)


# track cases where certain combinations of non-hidden options are invalid
incompatible_configs = [opt for opt in all_opts if is_incompatible(opt)]


directories = [GEN_SCRIPT_DIR, GEN_NOTEBOOK_DIR, TEST_TEMPLATE_DIR]

for directory in directories:
    # create the directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)

    # clear out the directory (to avoid confusion/running old scripts)
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

# lookup = {} # could probably be a list of dicts instead, but
data = all_opts.copy()

first_test_template_path = None

for datum in data:
    # save the rendered template
    rendered_template_stem = get_rendered_template_stem(datum, option_names)

    # datum["stem"] = rendered_template_stem # REVIEW: I don't think this is used

    if datum in incompatible_configs:
        datum[is_compatible_key] = False
        # REVIEW: consider adding logic that indicates why
        datum[rendered_key] = (
            "INVALID: The parameters you have selected are incompatible, either from not being implemented or being logically inconsistent."  # noqa E501
        )
        datum[preamble_key] = "\n"
        continue

    datum[is_compatible_key] = True

    # NOTE: Decided to always keep dummy key false for scripts, let dummy only
    # affect tests
    datum[DUMMY_KEY] = False

    script_template_name = "main.py.jinja"
    script_template = env.get_template(script_template_name)

    gen_script_name = f"{rendered_template_stem}.py"
    gen_script_path = path.join(GEN_SCRIPT_DIR, gen_script_name)

    render_datum = {var_name: datum[var_name] for var_name in jinja_var_names}
    script = script_template.render(render_datum)  # , names=constants

    # apply black formatting
    script = format_file_contents(script, fast=False, mode=FileMode())

    # be mindful of max file component length (255?), regardless of path limits
    # https://stackoverflow.com/a/61628356/13697228
    with open(gen_script_path, "w") as f:
        f.write(script)

    # make sure tests run faster for SAASBO
    test_render_datum = render_datum.copy()
    test_render_datum[DUMMY_KEY] = dummy
    model_kwargs = test_render_datum[MODEL_KWARGS_KEY]

    if "num_samples" in model_kwargs and "warmup_steps" in model_kwargs:
        model_kwargs["num_samples"] = 16
        model_kwargs["warmup_steps"] = 32

    test_script = script_template.render(test_render_datum)
    test_script = format_file_contents(test_script, fast=False, mode=FileMode())

    # indent each line by 4 spaces and prefix def test_script():
    four_spaces = "    "
    rendered_test_template = "def test_script():\n" + "\n".join(
        [four_spaces + line for line in test_script.split("\n")]
    )

    # append the if __name__ == "__main__": block
    rendered_test_template += "\n\nif __name__ == '__main__':\n    test_script()"

    # save in tests directory with test_ prefix
    test_template_path = path.join(TEST_TEMPLATE_DIR, f"test_{gen_script_name}")
    with open(test_template_path, "w") as f:
        f.write(rendered_test_template)

    # If this is the first iteration of the loop, store the test_template_path
    # NOTE: this is just to make debugging faster (i.e., skip FULLYBAYESIAN, etc.)
    if first_test_template_path is None:
        first_test_template_path = test_template_path

    datum[rendered_key] = script  # for the HTML template

    # store GitHub file link
    github_username = "sgbaird"
    github_prefix = f"https://github.com/{github_username}/honegumi/tree/main/"
    github_link = urljoin(github_prefix, gen_script_path)

    github_badge = f'<a href="{github_link}"><img alt="Open in GitHub" src="https://img.shields.io/badge/Open%20in%20GitHub-blue?logo=github&labelColor=grey"></a>'  # noqa E501

    colab_prefix = (
        "https://colab.research.google.com/github/sgbaird/honegumi/blob/main/"
    )

    notebook_path = path.join(GEN_NOTEBOOK_DIR, f"{rendered_template_stem}.ipynb")
    colab_link = urljoin(colab_prefix, notebook_path)
    colab_badge = f'<a href="{colab_link}"><img alt="Open In Colab" src="https://colab.research.google.com/assets/colab-badge.svg"></a>'  # noqa E501

    preamble = f"{colab_badge} {github_badge}"
    datum[preamble_key] = preamble  # for the HTML template

    # create an intermediate file object for gen_script and prepend colab link
    nb_text = f"# %% [markdown]\n{colab_badge}\n\n# %%\n%pip install ax-platform\n\n# %%\n{script}"  # noqa E501
    gen_script_file = io.StringIO(nb_text)

    # generate the notebook
    notebook = jupytext.read(gen_script_file, fmt="py:percent")

    with open(notebook_path, "w") as f:
        jupytext.write(notebook, f, fmt="notebook")

# run pytest on all or just one of the test scripts
collector = ResultsCollector()
file_filter = TEST_TEMPLATE_DIR if not dummy else first_test_template_path
# file_filter = TEST_TEMPLATE_DIR
retcode = pytest.main(["-v", file_filter], plugins=[collector])

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
    [str(opt[option_name]) for option_name in visible_option_names]
    for opt in invalid_configs
]

# NOTE: `custom_gen_opt_name` gets converted to a string from a boolean to
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
    if key not in df.columns:
        raise ValueError(f"key {key} not in {df.columns}")
    return {
        ",".join([str(opt[option_name]) for option_name in option_names]): opt[key]
        for opt in df.to_dict(orient="records")
    }


script_lookup = generate_lookup_dict(merged_df, visible_option_names, rendered_key)
preamble_lookup = generate_lookup_dict(merged_df, visible_option_names, preamble_key)


# Define the path to your HTML template file
template_path = "honegumi.html.jinja"

# Create a Jinja2 environment and load the template file
script_template = core_env.get_template(template_path)

# convert boolean values within option_rows to strings
jinja_option_rows = [row for row in visible_option_rows]
for row in jinja_option_rows:
    row["options"] = [str(opt) for opt in row["options"]]

# Render the template with your variables
html = script_template.render(
    jinja_option_rows=jinja_option_rows,
    script_lookup=script_lookup,
    preamble_lookup=preamble_lookup,
    invalid_configs=invalid_configs,
)

# Write the rendered HTML to a file
with open(path.join(DOC_DIR, "honegumi.html"), "w") as f:
    f.write(html)

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
