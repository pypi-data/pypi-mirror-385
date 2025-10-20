"""This module contains tests for ``tno.quantum.utils._base_arguments``."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, SupportsInt

import pytest

from tno.quantum.utils import BaseArguments
from tno.quantum.utils.serialization import check_serializable
from tno.quantum.utils.validation import check_kwarglike


# region define test arguments objects
@dataclass(init=False)
class GroundLevelArguments(BaseArguments):
    """
    Attributes:
        name: test name
        size: test size
    """

    name: str
    size: int

    def __init__(self, name: str = "test-name", size: SupportsInt = 5) -> None:
        self.name = name
        self.size = int(size)


@dataclass(init=False)
class NestedArguments(BaseArguments):
    """
    Attributes:
        nested_arguments: test name
    """

    nested_arguments: GroundLevelArguments = field(default_factory=GroundLevelArguments)

    def __init__(
        self,
        nested_arguments: GroundLevelArguments | Mapping[str, Any] | None = None,
    ) -> None:
        self.nested_arguments = (
            GroundLevelArguments.from_mapping(nested_arguments)
            if nested_arguments is not None
            else GroundLevelArguments()
        )


@dataclass(init=False)
class DoubleNestedArguments(BaseArguments):
    """
    Attributes:
        nested_arguments: test name
    """

    nested_arguments_1: NestedArguments = field(default_factory=NestedArguments)
    nested_arguments_2: GroundLevelArguments = field(
        default_factory=GroundLevelArguments
    )

    def __init__(
        self,
        nested_arguments_1: NestedArguments | Mapping[str, Any] | None = None,
        nested_arguments_2: GroundLevelArguments | Mapping[str, Any] | None = None,
    ) -> None:
        self.nested_arguments_1 = (
            NestedArguments.from_mapping(nested_arguments_1)
            if nested_arguments_1 is not None
            else NestedArguments()
        )
        self.nested_arguments_2 = (
            GroundLevelArguments.from_mapping(nested_arguments_2)
            if nested_arguments_2 is not None
            else GroundLevelArguments()
        )


@dataclass
class RequiredExampleArguments(BaseArguments):
    """
    Attributes:
        arg_without_default: test argument with no default
        arg_with_default_factory: test argument with default factory
    """

    arg_without_default: bool
    arg_with_default_factory: dict[str, Any] = field(default_factory=dict)


# region initialisation logic


def test_ground_level_arguments() -> None:
    """Test for an simple example `BaseArguments` class"""
    # Create GroundLevelArguments object
    name = "test-name"
    size = 5
    example_arguments = GroundLevelArguments(name=name, size=size)

    # Validate Arguments object remains kwargslike
    check_kwarglike(example_arguments, "example_arguments")
    size_example_arguments = 2
    assert len(example_arguments) == size_example_arguments

    # Validate getter
    assert example_arguments.name == name
    assert example_arguments.get("name") == name
    assert example_arguments["name"] == name

    assert example_arguments.size == size
    assert example_arguments.get("size") == size
    assert example_arguments["size"] == size

    # Validate raise KeyError
    with pytest.raises(KeyError):
        example_arguments["invalid_attribute"]

    # Validate iterator
    assert "name" in example_arguments
    assert "size" in example_arguments
    assert "test-name" in example_arguments.values()
    assert size in example_arguments.values()


def test_raise_extra_argument_warning() -> None:
    """Test raise warning when provided extra argument"""

    arguments_mapping = {
        "name": "test-name",
        "size": 5,
        "extra_key": "extra_value",
    }
    with pytest.warns(UserWarning, match="Ignoring unknown keys: extra_key"):
        GroundLevelArguments.from_mapping(arguments_mapping)


# region test from mapping


def test_from_mapping() -> None:
    """Test the from_mapping method"""
    name = "non-default-name"
    size = 6
    arguments_mapping = {
        "name": name,
        "size": size,
    }
    example_arguments = GroundLevelArguments.from_mapping(arguments_mapping)
    assert example_arguments.name == name
    assert example_arguments.size == size


def test_from_arguments() -> None:
    """Test the from_mapping method from Arguments"""
    name = "from_args"
    size = 11
    arguments_mapping = GroundLevelArguments(name=name, size=size)
    example_arguments = GroundLevelArguments.from_mapping(arguments_mapping)
    assert example_arguments.name == name
    assert example_arguments.size == size


def test_from_empty_mapping() -> None:
    """Test the from_mapping method for empty dict"""
    arguments_mapping: dict[str, Any] = {}
    example_arguments = GroundLevelArguments.from_mapping(arguments_mapping)

    ground_level_default_name = "test-name"
    ground_level_default_size = 5
    assert example_arguments.name == ground_level_default_name
    assert example_arguments.size == ground_level_default_size


def test_from_mapping_required_args() -> None:
    """Test the from_mapping method for required arguments"""
    arguments_mapping = {
        "arg_without_default": True,
        "arg_with_default_factory": {},
    }
    example_arguments = RequiredExampleArguments.from_mapping(arguments_mapping)
    assert example_arguments.arg_with_default_factory == {}
    assert example_arguments.arg_without_default is True

    # Test mapping with required args
    arguments_mapping = {"arg_without_default": True}
    example_arguments = RequiredExampleArguments.from_mapping(arguments_mapping)
    assert example_arguments.arg_with_default_factory == {}
    assert example_arguments.arg_without_default is True

    # Test missing argument without required value
    arguments_mapping = {}
    error_msg = "Missing required key: arg_without_default"
    with pytest.raises(KeyError, match=error_msg):
        RequiredExampleArguments.from_mapping(arguments_mapping)


def test_nested_base_arguments() -> None:
    """Test from_mapping for nested `BaseArguments`"""

    # Test from_mapping for an empty dict
    arguments_mapping: dict[str, Any] = {}
    arguments = DoubleNestedArguments.from_mapping(arguments_mapping)
    assert isinstance(arguments.nested_arguments_1, NestedArguments)
    assert isinstance(arguments.nested_arguments_2, GroundLevelArguments)
    assert isinstance(
        arguments.nested_arguments_1.nested_arguments, GroundLevelArguments
    )

    ground_level_default_name = "test-name"
    ground_level_default_size = 5
    assert (
        arguments.nested_arguments_1.nested_arguments.name == ground_level_default_name
    )
    assert (
        arguments.nested_arguments_1.nested_arguments.size == ground_level_default_size
    )
    assert arguments.nested_arguments_2.name == ground_level_default_name
    assert arguments.nested_arguments_2.size == ground_level_default_size

    # Test from_mapping for a filled dict
    arg1_size = 1
    arg1_name = "arg1-test-name"
    arg2_size = 2
    arg2_name = "arg2-test-name"
    arguments_mapping = {
        "nested_arguments_1": {
            "nested_arguments": {"name": arg1_name, "size": arg1_size}
        },
        "nested_arguments_2": {"name": arg2_name, "size": arg2_size},
    }
    arguments = DoubleNestedArguments.from_mapping(arguments_mapping)
    assert isinstance(arguments.nested_arguments_1, NestedArguments)
    assert isinstance(arguments.nested_arguments_2, GroundLevelArguments)
    assert isinstance(
        arguments.nested_arguments_1.nested_arguments, GroundLevelArguments
    )
    assert arguments.nested_arguments_1.nested_arguments.name == arg1_name
    assert arguments.nested_arguments_1.nested_arguments.size == arg1_size
    assert arguments.nested_arguments_2.name == arg2_name
    assert arguments.nested_arguments_2.size == arg2_size


# region Serializable


def test_arguments_serializable() -> None:
    """Test load JSON arguments from file."""
    check_serializable(GroundLevelArguments(name="test-json", size=2))
