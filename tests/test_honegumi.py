from honegumi.ax.utils import constants as cst
from honegumi.core._honegumi import (
    Honegumi,
    get_rendered_template_stem,
    main,
    unpack_rendered_template_stem,
)

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"


def test_honegumi():
    hg = Honegumi()
    hg.generate(**{cst.OBJECTIVE_OPT_KEY: "multi", cst.EXISTING_DATA_KEY: True})
    # hg.generate(objective="multi", existing_data=True)


def test_pydantic():
    from honegumi.ax._ax import option_rows

    hg = Honegumi(cst, option_rows)
    options_model = hg.OptionsModel(
        objective="multi", model="Default", custom_gen=False, existing_data=True
    )
    result = hg.generate(options_model)
    print(result)

    print(options_model.model_fields["objective"].json_schema_extra["hidden"])
    print(options_model.model_fields["objective"].json_schema_extra["disable"])

    # print(list(selections.model_fields.values())[0].json_schema_extra["hidden"])

    1 + 1


def test_get_deviating_options():

    option_names_shortlist = [
        "objective",
        "model",
        "custom_gen",
        "existing_data",
        "custom_threshold",
    ]

    current_config = {
        "objective": "single",
        "model": "Default",
        "custom_gen": False,
        "existing_data": False,
        "custom_threshold": False,
    }

    option_rows_short = [
        option for option in option_rows if option["name"] in option_names_shortlist
    ]

    hg = Honegumi(cst, option_rows_short, is_incompatible_fn=is_incompatible)

    deviating_options = hg.get_deviating_options(current_config)
    print(deviating_options)

    # Add assertions to verify the expected deviating options
    expected_deviating_options = {"custom_threshold": True}
    if deviating_options != expected_deviating_options:
        raise AssertionError(
            f"Expected deviating options: {expected_deviating_options}, but got: {deviating_options}"  # noqa: E501
        )

    1 + 1


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["7"])
    captured = capsys.readouterr()
    assert "The 7-th Fibonacci number is 13" in captured.out


if __name__ == "__main__":
    """Execute the test suite"""
    test_get_deviating_options()
    test_honegumi()
    # test_unpack_rendered_template_stem()


# %% Code Graveyard

# def test_results_collector():
#     collector = ResultsCollector()

#     # Test initial state
#     assert collector.reports == []
#     assert collector.collected == 0
#     assert collector.exitcode == 0
#     assert collector.passed == 0
#     assert collector.failed == 0
#     assert collector.xfailed == 0
#     assert collector.skipped == 0
#     assert collector.total_duration == 0

#     # Test pytest_runtest_makereport
#     class Item:
#         pass
#     class Call:
#         pass
#     item = Item()
#     call = Call()
#     report = pytest.Report(item=item, when='call', outcome='passed', duration=0.1,
#       longrepr=None,)
#     outcome = pytest.OutcomeReport(report=report)
#     generator = collector.pytest_runtest_makereport(item, call)
#     next(generator)
#     generator.send(outcome)
#     assert collector.reports == [report]

#     # Test pytest_collection_modifyitems
#     items = [1, 2, 3]
#     collector.pytest_collection_modifyitems(items)
#     assert collector.collected == 3

#     # Test pytest_terminal_summary
#     class TerminalReporter:
#         stats = {'passed': [1, 2], 'failed': [3], 'xfailed': [], 'skipped': []}
#     terminalreporter = TerminalReporter()
#     exitstatus = 0
#     collector.pytest_terminal_summary(terminalreporter, exitstatus)
#     assert collector.exitcode == exitstatus
#     assert collector.passed == 2
#     assert collector.failed == 1
#     assert collector.xfailed == 0
#     assert collector.skipped == 0
#     assert collector.total_duration > 0


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["7"])
    captured = capsys.readouterr()
    assert "The 7-th Fibonacci number is 13" in captured.out


if __name__ == "__main__":
    """Execute the test suite"""
    test_pydantic()
    test_unpack_rendered_template_stem()
