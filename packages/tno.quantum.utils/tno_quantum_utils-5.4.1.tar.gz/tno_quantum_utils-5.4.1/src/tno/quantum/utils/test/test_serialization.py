"""This module contains tests for ``tno.quantum.utils.serialization``."""

import importlib.util
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from tno.quantum.utils.serialization import Serializable, check_serializable


@dataclass
class Example(Serializable):
    none: None = field(default=None)
    boolean: bool = field(default=True)
    number: float = field(default=0.123)
    string: str = field(default="Hello world!")
    dic: dict[str, Any] = field(
        default_factory=lambda: {"i": 0, "f": 0.0, "b": False, "s": "0", "n": None}
    )
    lis: list[Any] = field(default_factory=lambda: [0, False, "0", 0.0, None])
    tup: tuple[Any, ...] = field(default_factory=lambda: (0, False, "0", 0.0, None))


@dataclass
class Nested(Serializable):
    example: Example
    example_list: list[Example]
    example_dict: dict[str, Example]


def test_serialization_basic() -> None:
    """Test basic (de)serialization."""
    example = Example(
        none=None,
        boolean=False,
        number=9.876,
        string="Good morning!",
        dic={"i": 1, "f": 1.0, "b": True, "s": "1", "n": None},
        lis=[1, True, "1", 1.0, None],
        tup=(1, True, "1", 1.0, None),
    )

    assert example == Serializable.from_json(example.to_json())
    assert example == Serializable.from_yaml(example.to_yaml())


def test_serialization_file() -> None:
    """Test (de)serialization to and from file."""
    example = Example(
        none=None,
        boolean=False,
        number=9.876,
        string="Good morning!",
        dic={"i": 1, "f": 1.0, "b": True, "s": "1", "n": None},
        lis=[1, True, "1", 1.0, None],
        tup=(1, True, "1", 1.0, None),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        # Test from JSON file
        temp_file_path = Path(temp_dir) / "test_file.json"
        example.to_json_file(temp_file_path)
        assert Serializable.from_json_file(temp_file_path) == example

        # Test from YAML file
        temp_file_path = Path(temp_dir) / "test_file.yaml"
        example.to_yaml_file(temp_file_path)
        assert Serializable.from_yaml_file(temp_file_path) == example


def test_serialization_nested() -> None:
    """Test (de)serialization of nested classes."""
    nested = Nested(
        example=Example(number=1.11),
        example_list=[Example(number=2.22)],
        example_dict={"key": Example(number=3.33)},
    )

    assert nested == Serializable.from_json(nested.to_json())
    assert nested == Serializable.from_yaml(nested.to_yaml())


@dataclass
class External:
    x: int


def test_serialization_external() -> None:
    """Test (de)serialization of external classes."""

    def serialize(value: External) -> dict[str, Any]:
        return {"custom_key": value.x}

    def deserialize(data: dict[str, Any]) -> External:
        return External(x=data["custom_key"])

    Serializable.register(External, serialize, deserialize)

    class_path = "utils.test.test_serialization.External"

    assert Serializable.serialize(External(x=13)) == {
        "__class__": class_path,
        "custom_key": 13,
    }

    assert Serializable.deserialize(
        {"__class__": class_path, "custom_key": 17}
    ) == External(x=17)


def test_serialization_error_dict_nonstr() -> None:
    """Test for error on serializing dict with non-string key."""
    with pytest.raises(NotImplementedError, match="dict with key of type"):
        Serializable.serialize({1: 2})


def test_serialization_error_nonserializable() -> None:
    """Test for error on serializing a non-serializable object."""
    with pytest.raises(NotImplementedError, match="serialize value of type"):
        Serializable.serialize(print)


def test_serialization_error_unexpected() -> None:
    """Test for error on deserializing object or incorrect type."""
    with pytest.raises(ValueError, match="but expected"):
        Nested.from_json(Example().to_json())


def test_serialization_error_unsupported_dict_class() -> None:
    """Test for error on deserializing dict with unsupported class."""
    with pytest.raises(NotImplementedError, match="deserialize class"):
        Serializable.deserialize({"__class__": "collections.abc.Callable"})


def test_serialization_error_unsupported_class() -> None:
    """Test for error on deserializing unsupported class."""
    with pytest.raises(NotImplementedError, match="Failed to deserialize type"):
        Serializable.deserialize(print)


def test_serialization_error_unknown_module() -> None:
    """Test for error on deserializing unknown class."""
    with pytest.raises(ModuleNotFoundError, match="could not import module"):
        Serializable.deserialize({"__class__": "x.y.z"})


def test_serialization_error_nonexistent_class() -> None:
    """Test for error on deserializing non-existent class."""
    with pytest.raises(ValueError, match="was not found in module"):
        Serializable.deserialize({"__class__": "tno.quantum.utils.NonExistent"})


def test_serialization_error_invalid_class() -> None:
    """Test for error on deserializing invalid class."""
    with pytest.raises(TypeError, match="is not a class"):
        Serializable.deserialize(
            {"__class__": "tno.quantum.utils.convert_to_snake_case"}
        )


def test_serialization_check_serializable() -> None:
    """Test if check_serializable passes for good Serializable classes."""
    nested = Nested(
        example=Example(number=1.11),
        example_list=[Example(number=2.22)],
        example_dict={"key": Example(number=3.33)},
    )
    check_serializable(nested)


class PrivateAttrs(Serializable):  # noqa: PLW1641
    def __init__(self, x: int) -> None:
        self._x = x

    @property
    def x(self) -> int:
        return self._x

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PrivateAttrs):
            return False
        return self._x == other._x


def test_serialization_private_attrs() -> None:
    """Test serialization for classes which store data in private attributes."""
    obj = PrivateAttrs(5)
    check_serializable(obj)


class MissingAttr(Serializable):
    def __init__(self, x: int) -> None:
        pass


def test_serialization_error_missing_attr() -> None:
    """Test if serialization fails for instance missing attribute required by init."""
    obj = MissingAttr(5)
    with pytest.raises(ValueError, match="missing attribute"):
        obj.serialize()


class Bad(Serializable):
    def __init__(self, x: int) -> None:
        self.x = x + 1


class AlsoBad(Serializable):
    def __init__(self, x: int) -> None:
        self.y = x


@pytest.mark.parametrize("unserializable_object", [print, Bad(13)])
def test_serialization_check_serializable_error_invalid_attribute(
    unserializable_object: Any,
) -> None:
    """Test if check_serializable fails for bad Serializable classes."""
    expected_msg = ""
    with pytest.raises(AssertionError, match=expected_msg):
        check_serializable(unserializable_object)


def test_serialization_check_serializable_error_missing_attribute() -> None:
    """Test if check_serializable fails for bad Serializable classes."""
    unserializable_object = AlsoBad(31)
    expected_msg = "missing attribute 'x' which is expected by __init__"
    with pytest.raises(ValueError, match=expected_msg):
        check_serializable(unserializable_object)


if importlib.util.find_spec("numpy") is not None:
    import numpy as np
    from numpy.random import RandomState
    from numpy.typing import NDArray

    @dataclass(eq=False)
    class Matrix(Serializable):  # noqa: PLW1641
        matrix_f64: NDArray[np.float64]
        matrix_u8: NDArray[np.uint8]
        matrix_bool: NDArray[np.bool_]

        def __eq__(self, other: Any) -> bool:
            if not isinstance(other, Matrix):
                return NotImplemented
            return (
                np.array_equal(self.matrix_f64, other.matrix_f64)
                and np.array_equal(self.matrix_u8, other.matrix_u8)
                and np.array_equal(self.matrix_bool, other.matrix_bool)
            )

    def test_serialization_ndarray() -> None:
        """Test (de)serialization of NumPy arrays."""
        matrix = Matrix(
            np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64),
            np.array([[1, 2, 3], [4, 5, 6]], dtype=np.uint8),
            np.array([[0, 2, 0], [4, 0, 6]], dtype=np.bool_),
        )
        matrix_json = matrix.to_json()
        assert matrix == Matrix.from_json(matrix_json)

    def test_serialization_random_state() -> None:
        """Test (de)serialization of RandomState."""
        state = RandomState(42)
        other: RandomState = Serializable.deserialize(Serializable.serialize(state))
        assert state.randint(2**31) == other.randint(2**31)


def test_serialization_complex() -> None:
    """Test (de)serialization of complex."""
    value = 3 + 2j
    serialized_value = Serializable.serialize(value)
    assert serialized_value["real"] == value.real
    assert serialized_value["imag"] == value.imag
    assert value == Serializable.deserialize(serialized_value)
