"""This module contains tests for ``tno.quantum.utils._utils``."""

from typing import Any

import numpy as np
import pytest

from tno.quantum.utils import (
    check_equal,
    convert_to_snake_case,
    get_installed_subclasses,
)
from tno.quantum.utils.validation import check_snake_case


class BaseModel:
    """Dummy base model"""

    def __init__(self, arg1: int, arg2: int) -> None:
        self.arg1 = arg1
        self.arg2 = arg2


class ModelA(BaseModel):
    """Model A (supported)"""


class ModelB(BaseModel):
    """Model B (supported)"""


class ModelC:
    """Model C (not supported)"""


def test_get_supported_subclasses() -> None:
    """Test get supported models for dummy models"""

    supported_subclasses = get_installed_subclasses("utils.test.test_utils", BaseModel)

    assert "model_a" in supported_subclasses
    assert "model_b" in supported_subclasses
    assert "model_c" not in supported_subclasses


@pytest.mark.parametrize(
    ("x", "expected_output"),
    [
        ("a", "a"),
        ("A", "a"),
        ("StronglyEntangledModel", "strongly_entangled_model"),
        ("BasicModel", "basic_model"),
        ("QModel", "q_model"),
        ("TESTTwoWords", "test_two_words"),
        ("ModelA", "model_a"),
        ("Model with spaces", "model_with_spaces"),
        ("Model-with mixed--multiple  spaces", "model_with_mixed_multiple_spaces"),
    ],
)
def test_convert_to_snake(x: str, expected_output: str) -> None:
    """Test convert to snake case helper function."""
    converted_x = convert_to_snake_case(x)
    assert converted_x == expected_output
    assert check_snake_case(converted_x, "converted_x")


@pytest.mark.parametrize(
    "x",
    ["1abc", "!abc", "#aa", ".aa", "~bb"],
)
def test_convert_to_snake_raise_error_first_char_invalid(x: str) -> None:
    """Test raise error convert to snake case helper function."""
    error_msg = "Input cannot start with a number or any special symbol"
    with pytest.raises(ValueError, match=error_msg):
        convert_to_snake_case(x)


@pytest.mark.parametrize(
    "x",
    ["abc!", "aa#aa", "default.value", "when~bb"],
)
def test_convert_to_snake_raise_error_special_char_invalid(x: str) -> None:
    """Test raise error convert to snake case helper function."""
    error_msg = "Input cannot contain special characters."
    with pytest.raises(ValueError, match=error_msg):
        convert_to_snake_case(x)


def test_convert_to_snake_path() -> None:
    """Test path flag of convert to snake case."""
    x = "default.value"
    converted_x = convert_to_snake_case(x, path=True)
    assert converted_x == "default.value"
    assert check_snake_case(converted_x, "converted_x", path=True)


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        (1, 1, True),
        (0, 1, False),
        (
            {"c": {"d": [5]}, "b": [2, 3], "a": 1},
            {"a": 1, "b": [2, 3], "c": {"d": [5]}},
            True,
        ),
        (
            {"c": {"d": [6]}, "b": [2, 3], "a": 1},
            {"a": 1, "b": [2, 3], "c": {"d": [5]}},
            False,
        ),
        (
            np.array([[1, 0], [0, 1]], dtype=np.float64),
            np.array([[1, 0], [0, 1]], dtype=np.int32),
            True,
        ),
        (
            np.array([[1, 0], [0, 1]], dtype=np.float64),
            np.array([[0, 1], [1, 0]], dtype=np.float64),
            False,
        ),
        (None, None, True),
        (0, None, False),
        ("a", "a", True),
        ("b", "c", False),
    ],
)
def test_check_equal(first: Any, second: Any, expected: bool) -> None:
    """Test the check_equal method."""
    assert check_equal(first, second) == expected
