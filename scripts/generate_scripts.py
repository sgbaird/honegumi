import time
from itertools import product
from os import path
from pathlib import Path

import pytest
from ax.modelbridge.factory import Models
from black import FileMode, format_file_contents
from jinja2 import Environment, FileSystemLoader

from honegumi.ax.utils.constants import (
    gen_template_dir,
    model_opt_name,
    objective_opt_name,
    template_dir,
    test_template_dir,
    use_custom_gen_opt_name,
)

env = Environment(loader=FileSystemLoader(template_dir))

# opts stands for options
allowable_opts = {
    objective_opt_name: ["single", "multi"],
    model_opt_name: [Models.GPEI.name, Models.FULLYBAYESIAN.name],
    use_custom_gen_opt_name: [True, False],
}

# E.g.,
# {
#     "objective": ["single", "multi"],
#     "model": ["GPEI", "FULLYBAYESIAN"],
#     "use_custom_gen": [True, False],
# }

option_names = list(allowable_opts.keys())
# create all combinations of objective_opts and model_opts while retaining keys
# make it scalable to more option combinations
all_opts = [dict(zip(allowable_opts, v)) for v in product(*allowable_opts.values())]

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
Path(test_template_dir).mkdir(parents=True, exist_ok=True)


# rendered_templates = {}

for data in all_opts:
    template_name = "main.py.jinja"
    template = env.get_template(template_name)

    # save the rendered template
    rendered_template_stem = "__".join(
        [f"{option_name}-{str(data[option_name])}" for option_name in option_names]
    )

    gen_template_name = f"{rendered_template_stem}.py"
    gen_template_path = path.join(gen_template_dir, gen_template_name)

    rendered_template = template.render(data)
    # apply black formatting
    rendered_template = format_file_contents(
        rendered_template, fast=False, mode=FileMode()
    )

    # rendered_templates[rendered_template_stem] = rendered_template
    data["rendered_template"] = rendered_template

    with open(gen_template_path, "w") as f:
        f.write(rendered_template)

    # indent each line by 4 spaces and prefix def test_script():
    rendered_test_template = "def test_script():\n" + "\n".join(
        ["    " + line for line in rendered_template.split("\n")]
    )

    # save in tests directory with test_ prefix
    test_template_path = path.join(test_template_dir, f"test_{gen_template_name}")
    with open(test_template_path, "w") as f:
        f.write(rendered_test_template)

# # write data to json file
# with open(path.join("data", "processed", "data.json"), "w") as f:
#     json.dump(all_opts, f, indent=4)

# # write rendered_templates to json file
# with open(path.join("data", "processed", "rendered_templates.json"), "w") as f:
#     json.dump(rendered_templates, f, indent=4)

# run pytest on one of the test scripts


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        print(exitstatus, dir(exitstatus))
        self.exitcode = exitstatus
        self.passed = len(terminalreporter.stats.get("passed", []))
        self.failed = len(terminalreporter.stats.get("failed", []))
        self.xfailed = len(terminalreporter.stats.get("xfailed", []))
        self.skipped = len(terminalreporter.stats.get("skipped", []))

        self.total_duration = time.time() - terminalreporter._sessionstarttime


collector = ResultsCollector()
retcode = pytest.main(["-v", test_template_path], plugins=[collector])
for report in collector.reports:
    print("id:", report.nodeid, "outcome:", report.outcome)  # etc
print("exit code:", collector.exitcode)
print(
    "passed:",
    collector.passed,
    "failed:",
    collector.failed,
    "xfailed:",
    collector.xfailed,
    "skipped:",
    collector.skipped,
)
print("total duration:", collector.total_duration)


# pytest.main(["-v", test_template_dir])

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
