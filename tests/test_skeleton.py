import pytest

from honegumi.core.skeleton import (
    fib,
    get_rendered_template_stem,
    main,
    unpack_rendered_template_stem,
)

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"


def test_fib():
    """API Tests"""
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)


def test_get_rendered_template_stem():
    # Test case 1: Single option
    data = {"option1": "value1"}
    option_names = ["option1"]
    expected_output = "option1-value1"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 2: Multiple options
    data = {"option1": "value1", "option2": "value2", "option3": "value3"}
    option_names = ["option1", "option2", "option3"]
    expected_output = "option1-value1__option2-value2__option3-value3"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 3: Boolean option
    data = {"option1": True}
    option_names = ["option1"]
    expected_output = "option1-True"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 4: Integer option
    data = {"option1": 123}
    option_names = ["option1"]
    expected_output = "option1-123"
    assert get_rendered_template_stem(data, option_names) == expected_output

    # Test case 5: Empty option list
    data = {"option1": "value1"}
    option_names = []
    expected_output = ""
    assert get_rendered_template_stem(data, option_names) == expected_output


def test_unpack_rendered_template_stem():
    # Test case 1: Single option
    rendered_template_stem = "option1-value1"
    expected_output = {"option1": ["value1"]}
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # Test case 2: Multiple options
    rendered_template_stem = "option1-value1__option2-value2__option3-value3"
    expected_output = {
        "option1": ["value1"],
        "option2": ["value2"],
        "option3": ["value3"],
    }
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # Test case 3: Multiple values for the same option
    rendered_template_stem = "option1-value1__option1-value2"
    expected_output = {"option1": ["value1", "value2"]}
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output

    # Test case 4: Empty input
    rendered_template_stem = ""
    expected_output = {}
    assert unpack_rendered_template_stem(rendered_template_stem) == expected_output


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["7"])
    captured = capsys.readouterr()
    assert "The 7-th Fibonacci number is 13" in captured.out
