import os
from os import path
from pathlib import Path

import pandas as pd
import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

import honegumi.ax.utils.constants as cst
from honegumi.ax._ax import (
    add_model_specific_keys,
    extra_jinja_var_names,
    is_incompatible_ax,
    model_kwargs_test_override,
    option_rows,
    tooltips,
)
from honegumi.core._honegumi import (
    ResultsCollector,
    create_and_clear_dir,
    create_notebook,
    gen_combs_with_keys,
    generate_lookup_dict,
    generate_script,
    generate_test,
    prep_datum_for_render,
    unpack_rendered_template_stem,
)

# NOTE: `from ax.modelbridge.factory import Models` causes an issue with pytest!
# i.e., hard-code the model names instead of accessing them programatically
# see https://github.com/facebook/Ax/issues/1781

dummy = os.getenv("SMOKE_TEST", "False").lower() == "true"
skip_tests = os.getenv("SKIP_TESTS", "False").lower() == "true"

if dummy:
    print("DUMMY RUN / SMOKE TEST FOR FASTER DEBUGGING")

if skip_tests:
    print("SKIPPING TESTS")

env = Environment(
    loader=FileSystemLoader(cst.TEMPLATE_DIR),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)
core_env = Environment(
    loader=FileSystemLoader(cst.CORE_TEMPLATE_DIR),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)

# remove the options where disable is True, and print disabled options (keep
# track of disabled option names and default values)
disabled_option_defaults = [
    {row["name"]: row["options"][0]} for row in option_rows if row["disable"]
]
disabled_option_names = [row["name"] for row in option_rows if row["disable"]]

option_rows = [row for row in option_rows if not row["disable"]]

if disabled_option_defaults:
    print("The following options have been disabled:")
    for default in disabled_option_defaults:
        print(f"Disabled option and default: {default}")


for row in option_rows:
    if row["name"] in tooltips:
        row["tooltip"] = tooltips[row["name"]]

# E.g.,
# {
#     "objective": ["single", "multi"],
#     "model": ["GPEI", "FULLYBAYESIAN"],
#     "use_custom_gen": [True, False],
# }

option_names = [row["name"] for row in option_rows]

visible_option_names = [row["name"] for row in option_rows if not row["hidden"]]
visible_option_rows = [row for row in option_rows if not row["hidden"]]

jinja_var_names = option_names + extra_jinja_var_names + disabled_option_names

jinja_option_rows = [row for row in visible_option_rows]


all_opts = gen_combs_with_keys(visible_option_names, visible_option_rows)


for opt in all_opts:
    # set the default values for the disabled options
    for default in disabled_option_defaults:
        opt.update(default)

    # in-place operation
    add_model_specific_keys(option_names, opt)


directories = [cst.GEN_SCRIPT_DIR, cst.GEN_NOTEBOOK_DIR, cst.TEST_TEMPLATE_DIR]


[create_and_clear_dir(directory) for directory in directories]

# lookup = {} # could probably be a list of dicts instead
data = all_opts.copy()

first_test_template_path = None


for datum in data:
    # save the rendered template

    prep_datum_for_render(option_names, datum, is_incompatible_fn=is_incompatible_ax)

    if not datum[cst.IS_COMPATIBLE_KEY]:
        datum[cst.RENDERED_KEY] = (
            "INVALID: The parameters you have selected are incompatible, either from not being implemented or being logically inconsistent."  # noqa E501
        )
        datum[cst.PREAMBLE_KEY] = "\n"
        # skip rendering the script, test, and notebook
        continue

    script_template_name = "main.py.jinja"
    script_template = env.get_template(script_template_name)

    script, render_datum = generate_script(jinja_var_names, datum, script_template)

    datum[cst.RENDERED_KEY] = script  # for the HTML template

    gen_script_name = f"{datum['stem']}.py"
    gen_script_path = path.join(cst.GEN_SCRIPT_DIR, gen_script_name)

    # be mindful of max file component length (255?), regardless of path limits
    # https://stackoverflow.com/a/61628356/13697228
    with open(gen_script_path, "w") as f:
        f.write(script)

    # make sure tests run faster for SAASBO

    rendered_test_template = generate_test(
        script_template,
        render_datum,
        dummy=dummy,
        render_datum_override_fn=model_kwargs_test_override,
    )

    # save in tests directory with test_ prefix
    test_template_path = path.join(cst.TEST_TEMPLATE_DIR, f"test_{gen_script_name}")

    with open(test_template_path, "w") as f:
        f.write(rendered_test_template)

    # If this is the first iteration of the loop, store the test_template_path
    # NOTE: this is just to make debugging faster (i.e., skip FULLYBAYESIAN, etc.)
    if first_test_template_path is None:
        first_test_template_path = test_template_path

    notebook, notebook_path = create_notebook(datum, gen_script_path, script)

data_df = pd.DataFrame(data)

if not skip_tests:
    print("Running tests...")

    # run pytest on all or just one of the test scripts
    collector = ResultsCollector()
    file_filter = cst.TEST_TEMPLATE_DIR if not dummy else first_test_template_path
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
else:
    report_df = None

# concatenate the two dataframes to merge the columns based on option_names
# (i.e., the keys)
if report_df is not None:
    merged_df = pd.merge(data_df, report_df, on=option_names, how="outer")
else:
    merged_df = data_df.copy()
    merged_df["passed"] = True

# find the configs that either failed or were incompatible

invalid_configs = merged_df[
    (merged_df["passed"] == False) | (merged_df[cst.IS_COMPATIBLE_KEY] == False)  # noqa
][option_names].to_dict(orient="records")

# extract the values for each option name
invalid_configs = [
    [str(opt[option_name]) for option_name in visible_option_names]
    for opt in invalid_configs
]

script_lookup = generate_lookup_dict(merged_df, visible_option_names, cst.RENDERED_KEY)
preamble_lookup = generate_lookup_dict(
    merged_df, visible_option_names, cst.PREAMBLE_KEY
)


# Define the path to your HTML template file
template_path = "honegumi.html.jinja"

# Create a Jinja2 environment and load the template file
script_template = core_env.get_template(template_path)

# convert boolean values within option_rows to strings
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
with open(path.join(cst.DOC_DIR, "honegumi.html"), "w") as f:
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

# # track cases where certain combinations of non-hidden options are invalid
# incompatible_configs = [opt for opt in all_opts if is_incompatible_ax(opt)]
