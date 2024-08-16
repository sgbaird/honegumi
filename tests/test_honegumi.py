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
    GenerateOptions = hg.OptionsModel
    selections = GenerateOptions(
        objective="multi", model="Default", custom_gen=False, existing_data=True
    )
    result = hg.generate(selections)
    print(result)

    print(selections.model_fields["objective"].json_schema_extra["hidden"])
    print(selections.model_fields["objective"].json_schema_extra["disable"])

    # print(list(selections.model_fields.values())[0].json_schema_extra["hidden"])

    1 + 1


def test_get_rendered_template_stem():
    # Test case 1: Single option
    data = {"option1": "value1"}
    option_names = ["option1"]
    expected_output = "option1-value1"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 2: Multiple options
    data = {"option1": "value1", "option2": "value2", "option3": "value3"}
    option_names = ["option1", "option2", "option3"]
    expected_output = "option1-value1+option2-value2+option3-value3"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 3: Boolean option (True)
    data = {"option1": True}
    option_names = ["option1"]
    expected_output = "option1-True"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 4: Boolean option (False)
    data = {"option1": False}
    option_names = ["option1"]
    expected_output = "option1-False"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 5: Integer option
    data = {"option1": 123}
    option_names = ["option1"]
    expected_output = "option1-123"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 6: Empty option list
    data = {"option1": "value1"}
    option_names = []
    expected_output = ""
    assert get_rendered_template_stem(data, option_names) == expected_output


def test_unpack_rendered_template_stem():
    # Test case 1: Single option
    rendered_template_stem = "option1-value1"
    expected_output = {"option1": "value1"}
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # Test case 2: Multiple options
    rendered_template_stem = "option1-value1+option2-value2+option3-value3"
    expected_output = {
        "option1": "value1",
        "option2": "value2",
        "option3": "value3",
    }
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # # Test case 3: Multiple values for the same option
    # rendered_template_stem = "option1-value1__option1-value2"
    # expected_output = {"option1": ["value1", "value2"]}
    # assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # # Test case 4: Empty input
    # rendered_template_stem = ""
    # expected_output = {}
    # assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # Test case 1: Boolean string "True"
    rendered_template_stem = "option1-True"
    expected_output = {"option1": True}
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # Test case 2: Boolean string "False"
    rendered_template_stem = "option1-False"
    expected_output = {"option1": False}
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output


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
