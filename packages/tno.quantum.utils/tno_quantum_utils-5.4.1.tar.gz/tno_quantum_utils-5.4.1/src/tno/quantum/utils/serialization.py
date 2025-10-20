"""This module contains the :py:class:`Serializable` class.

The module provides the tools to give any class support for default serialization and
deserialization.

For example, when defining a class that inherits from :py:class:`Serializable`, methods
such as :py:meth:`~Serializable.to_json` and :py:meth:`~Serializable.from_json` are
automatically added to the class.

    >>> from tno.quantum.utils.serialization import Serializable
    >>>
    >>> # Define a class that inherits from Serializable
    >>> class Point(Serializable):
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    ...     def __repr__(self):
    ...         return f"Point(x={self.x}, y={self.y})"
    >>>
    >>> # Create an instance and serialize to JSON
    >>> point = Point(1, 2)
    >>> point_json = point.to_json()
    >>> print(point_json)  # doctest: +ELLIPSIS
    {"x": 1, "y": 2, "__class__": "..."}
    >>>
    >>> # Deserialize JSON to instance of Point
    >>> Point.from_json(point_json)  # doctest: +SKIP
    Point(x=1, y=2)

.. note::
   By default, serialization is performed by storing the attributes of a class as found
   in the :py:const:`__init__` of the class. Therefore, make sure your class has
   attributes that match the signature of the constructor of your class.

Information about the class is stored in the serialized data, so that it is possible to
deserialize without knowing the target class. For example:

    >>> Serializable.from_json(point_json)  # doctest: +SKIP
    Point(x=1, y=2)

If your class contains attributes which are instances of third-party classes, it is
possible to register serialization and deserialization methods for these third-party
classes. For example, (de)serialization methods for NumPy arrays are registered (by
default) as follows:

    >>> import numpy as np
    >>> from numpy.typing import NDArray
    >>>
    >>> def serialize_ndarray(value: NDArray[Any]) -> dict[str, Any]:
    ...     return {"dtype": str(value.dtype), "array": value.tolist()}
    >>>
    >>> def deserialize_ndarray(data: dict[str, Any]) -> NDArray[Any]:
    ...     dtype = np.dtype(data["dtype"])
    ...     array = data["array"]
    ...     return np.array(array, dtype=dtype)
    >>>
    >>> Serializable.register(np.ndarray, serialize_ndarray, deserialize_ndarray)

NumPy arrays will now automatically be (de)serialized, as in the following example:

    >>> class LinearSystem(Serializable):
    ...     matrix: NDArray[np.float64]
    ...     vector: NDArray[np.float64]
    ...
    ...     def __init__(self, matrix, vector):
    ...         self.matrix = matrix
    ...         self.vector = vector
    ...
    ...     def __repr__(self):
    ...         return f"LinearSystem(matrix={self.matrix}, vector={self.vector})"
    >>>
    >>> system = LinearSystem(np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([1.0, 1.0]))
    >>> system_json = system.to_json()
    >>> print(system_json)  # doctest: +ELLIPSIS
    {"matrix": {"dtype": "float64", "array": [[1.0, 2.0], [3.0, 4.0]], "__class__": "numpy.ndarray"}, "vector": {"dtype": "float64", "array": [1.0, 1.0], "__class__": "numpy.ndarray"}, "__class__": "..."}
    >>>
    >>> Serializable.from_json(system_json)  # doctest: +SKIP
    LinearSystem(matrix=[[1. 2.]
    [3. 4.]], vector=[1. 1.])

    .. note::
        Instances of classes are (de)serialized to and from :py:const:`dict`'s via the
        private methods :py:const:`Serializable._serialize(self) -> dict[str, Any]` and
        :py:const:`Serializable._deserialize(cls, data: dict[str, Any]) -> Any`. If your
        class requires special (de)serialization, it is possible to override these
        methods in your class. These must be implemented in such a way that they are
        inverse to each other.
"""  # noqa: E501

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import tempfile
import warnings
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any

import yaml

from tno.quantum.utils.validation import check_path

_externals: dict[
    str, tuple[Callable[[Any], dict[str, Any]], Callable[[dict[str, Any]], Any]]
] = {}


class Serializable:
    """Framework for serializable objects."""

    def to_json(self, *, indent: int | None = None) -> str:
        """Serialize to JSON.

        Args:
            indent: If provided, JSON will be pretty-printed with given indent level.

        Returns:
            JSON string.
        """
        return json.dumps(self.serialize(), indent=indent)

    def to_yaml(self) -> str:
        """Serialize to YAML.

        Returns:
            YAML string.
        """
        return yaml.dump(self.serialize(), Dumper=yaml.Dumper)

    def to_json_file(self, path: str | Path, *, indent: int | None = None) -> None:
        """Serialize and write to JSON file.

        Args:
            path: Path of the file to write to.
            indent: If provided, JSON will be pretty-printed with given indent level.
        """
        path = check_path(
            path,
            "path",
            must_exist=False,
            required_suffix=".json",
            safe=True,
        )
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.serialize(), file, indent=indent)

    def to_yaml_file(self, path: str | Path) -> None:
        """Serialize and write to YAML file.

        Args:
            path: Path of the file to write to.
        """
        path = check_path(
            path,
            "path",
            must_exist=False,
            required_suffix=".yaml",
            safe=True,
        )
        with path.open("w", encoding="utf-8") as file:
            yaml.dump(self.serialize(), file)

    def serialize(self: Any) -> Any:
        """Serialize self to dict, list or primitive.

        Returns:
            Representation of self as dict, list, string, boolean or ``None``.
        """
        value = self

        # bool, str, None, int, float
        if type(value) in [bool, str, type(None), int, float]:
            return value

        # list
        if type(value) is list:
            return [Serializable.serialize(x) for x in value]

        # tuple
        if type(value) is tuple:
            return {"__tuple__": [Serializable.serialize(x) for x in value]}

        # dict
        if type(value) is dict:
            dict_ = {}
            for key, val in value.items():
                if not isinstance(key, str):
                    msg = f"Could not serialize dict with key of type {type(key)}"
                    raise NotImplementedError(msg)
                dict_[key] = Serializable.serialize(val)
            return dict_

        # Serializable
        if isinstance(value, Serializable):
            dict_ = value._serialize()  # noqa: SLF001
            dict_["__class__"] = Serializable._class_to_path(value.__class__)
            return dict_

        # External
        if external := Serializable._get_external(value.__class__):
            dict_ = external[0](value)
            dict_["__class__"] = Serializable._class_to_path(value.__class__)
            return dict_

        msg = f"Could not serialize value of type {type(value)}"
        raise NotImplementedError(msg)

    def _serialize(self) -> dict[str, Any]:
        """Serialize to dict.

        Classes derived from ``Serializable`` may override this method for custom
        serialization. In this case, override ``_deserialize`` accordingly.
        """
        init_signature = inspect.signature(self.__class__.__init__)
        init_args = [parameter.name for parameter in init_signature.parameters.values()]
        init_args = init_args[1:]  # remove first argument `self`

        dict_ = {}
        for key in init_args:
            if not hasattr(self, key):
                msg = (
                    f"Failed to serialize value of type {type(self)}: missing "
                    f"attribute '{key}' which is expected by __init__ of {type(self)}"
                )
                raise ValueError(msg)
            dict_[key] = Serializable.serialize(getattr(self, key))
        return dict_

    @classmethod
    def from_json(cls, data: str) -> Any:
        """Deserialize from JSON.

        Args:
            data: JSON string to deserialize.

        Returns:
            Deserialized instance of `cls`.

        Raises:
            ValueError: If `data` is ill-formed.
            NotImplementedError: If no deserialization method exists to deserialize.
        """
        return Serializable._deserialize_class(cls, json.loads(data))

    @classmethod
    def from_yaml(cls, data: str) -> Any:
        """Deserialize from YAML.

        Args:
            data: YAML string to deserialize.

        Returns:
            Deserialized instance of `cls`.

        Raises:
            ValueError: If `data` is ill-formed.
            NotImplementedError: If no deserialization method exists to deserialize.
        """
        return Serializable._deserialize_class(cls, yaml.safe_load(data))

    @classmethod
    def from_json_file(cls, path: str | Path) -> Any:
        """Read and deserialize from JSON file.

        Args:
            path: Path to JSON file to deserialize.

        Returns:
            Deserialized instance of `cls`.

        Raises:
            ValueError: If `data` is ill-formed.
            NotImplementedError: If no deserialization method exists to deserialize.
            FileNotFoundError: If file at `path` not found.
        """
        path = check_path(
            path,
            "path",
            must_exist=True,
            must_be_file=True,
            required_suffix=".json",
            safe=True,
        )
        with path.open("r", encoding="utf-8") as file:
            return Serializable._deserialize_class(cls, json.load(file))

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> Any:
        """Read and deserialize from YAML file.

        Args:
            path: Path to YAML file to deserialize.

        Returns:
            Deserialized instance of `cls`.

        Raises:
            ValueError: If `data` is ill-formed.
            NotImplementedError: If no deserialization method exists to deserialize.
            FileNotFoundError: If file at `path` not found.
        """
        path = check_path(
            path,
            "path",
            must_exist=True,
            must_be_file=True,
            required_suffix=".yaml",
            safe=True,
        )
        with path.open("r", encoding="utf-8") as file:
            return Serializable._deserialize_class(cls, yaml.safe_load(file))

    @staticmethod
    def _deserialize_class(class_obj: type[Serializable], data: Any) -> Any:
        """Deserialize data into an instance of `class_obj`.

        Returns:
            Deserialized instance of type `class_obj`.

        Raises:
            ValueError: If deserialized instance is not of type `class_obj`.
        """
        deserialized_obj = Serializable.deserialize(data)
        if class_obj is not Serializable and not isinstance(
            deserialized_obj, class_obj
        ):
            msg = (
                f"Deserialized object of type {type(deserialized_obj)},"
                f" but expected {class_obj}"
            )
            raise ValueError(msg)
        return deserialized_obj

    @staticmethod
    def deserialize(data: Any) -> Any:
        """Deserialize data.

        Returns:
            Deserialized object.
        """
        # bool, str, None, int, float
        if type(data) in [bool, str, type(None), int, float]:
            return data

        # list
        if type(data) is list:
            return [Serializable.deserialize(x) for x in data]

        if type(data) is dict:
            # tuple
            tuple_data = data.pop("__tuple__", None)
            if tuple_data is not None:
                if type(tuple_data) is not list:
                    msg = f"Failed to deserialize tuple, got {type(tuple_data)}"
                    raise ValueError(msg)
                return tuple(Serializable.deserialize(value) for value in tuple_data)

            # dict
            cls_path = data.pop("__class__", None)
            if cls_path is None:
                return {
                    key: Serializable.deserialize(value) for key, value in data.items()
                }

            cls = Serializable._class_from_path(cls_path)

            # Serializable
            if issubclass(cls, Serializable):
                return cls._deserialize(data)

            # External classes
            if external := Serializable._get_external(cls):
                return external[1](data)

            msg = f"Could not deserialize class {cls_path}"
            raise NotImplementedError(msg)

        msg = f"Failed to deserialize type {type(data)}"
        raise NotImplementedError(msg)

    @classmethod
    def _deserialize(cls, data: dict[str, Any]) -> Any:
        """Deserialize data into an instance of `cls`.

        Classes derived from ``Serializable`` may override this method for custom
        deserialization. In this case, override ``_serialize`` accordingly.
        """
        data = {key: Serializable.deserialize(value) for key, value in data.items()}
        return cls(**data)

    @staticmethod
    def register(
        class_obj: type,
        serialize: Callable[[Any], dict[str, Any]],
        deserialize: Callable[[dict[str, Any]], Any],
    ) -> None:
        """Register serialization and deserialization functions for external class.

        Args:
            class_obj: Class to be serialized and deserialized.
            serialize: Function that serializes instances of class `cls`.
            deserialize: Function that deserializes into instance of class `cls`.
        """
        cls_name = Serializable._class_to_path(class_obj)
        if cls_name in _externals:
            msg = f"Serialization functions for class {class_obj} already provided"
            warnings.warn(msg, stacklevel=2)
        _externals[cls_name] = (serialize, deserialize)

    @staticmethod
    def _get_external(
        class_obj: type,
    ) -> tuple[Callable[[Any], dict[str, Any]], Callable[[dict[str, Any]], Any]] | None:
        """Get external serialization and deserialization functions for `cls`.

        Returns ``None`` if they do not exist.
        """
        cls_name = Serializable._class_to_path(class_obj)
        if cls_name in _externals:
            return _externals[cls_name]
        return None

    @staticmethod
    def _class_to_path(class_obj: type) -> str:
        """Construct path of class."""
        return f"{class_obj.__module__}.{class_obj.__name__}"

    @staticmethod
    def _class_from_path(cls_path: str) -> Any:
        """Obtain class from its path."""
        module_name, class_name = cls_path.rsplit(".", 1)

        if module_name == "":
            msg = "Failed to deserialize because module name is empty"
            raise ValueError(msg)

        if module_name.startswith("."):
            msg = f"Failed to deserialize because module name {module_name} is relative"
            raise ValueError(msg)

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as err:
            msg = f"Failed to deserialize because could not import module {module_name}"
            raise ModuleNotFoundError(msg) from err

        if not hasattr(module, class_name):
            msg = (
                f"Failed to deserialize because class {class_name} "
                f"was not found in module {module_name}"
            )
            raise ValueError(msg)

        cls = getattr(module, class_name, None)
        if not isinstance(cls, type):
            msg = f"Failed to deserialize because {class_name} is not a class"
            raise TypeError(msg)

        return cls

    def __eq__(self, other: Any) -> bool:
        """Check object equality.

        This is the default equality check for serializable objects, where two objects
        are considered equal if they are of the same type and produce the same
        serialization.
        """
        if not isinstance(other, Serializable):
            return False
        if type(self) is not type(other):
            return False
        return self._serialize() == other._serialize()

    def __hash__(self) -> int:
        """Compute object hash.

        This is the default hash function for serializable objects, where the hash
        of an object is computed as a function of its serialization only.
        """
        return hash(json.dumps(self._serialize(), sort_keys=True, ensure_ascii=True))


if importlib.util.find_spec("numpy") is not None:
    import numpy as np
    from numpy.random import RandomState
    from numpy.typing import NDArray

    # Register `numpy.ndarray` as serializable
    def _serialize_ndarray(value: NDArray[Any]) -> dict[str, str | list[Any]]:
        return {"dtype": str(value.dtype), "array": value.tolist()}

    def _deserialize_ndarray(data: dict[str, Any]) -> NDArray[Any]:
        dtype = np.dtype(data["dtype"])
        array = data["array"]
        return np.array(array, dtype=dtype)

    Serializable.register(np.ndarray, _serialize_ndarray, _deserialize_ndarray)

    # Register `'numpy.random.mtrand.RandomState'` as serializable
    def _serialize_random_state(value: RandomState) -> dict[str, str | list[Any]]:
        return {"state": [Serializable.serialize(v) for v in value.get_state()]}

    def _deserialize_random_state(data: dict[str, Any]) -> RandomState:
        state = tuple(Serializable.deserialize(v) for v in data["state"])
        rng = RandomState()
        rng.set_state(state)
        return rng

    Serializable.register(
        RandomState, _serialize_random_state, _deserialize_random_state
    )


# Register `timedelta` as serializable
def _serialize_timedelta(time: timedelta) -> dict[str, float]:
    return {"seconds": time.total_seconds()}


def _deserialize_timedelta(data: dict[str, float]) -> timedelta:
    return timedelta(seconds=data["seconds"])


Serializable.register(timedelta, _serialize_timedelta, _deserialize_timedelta)


# Register `complex` as serializable
def _serialize_complex(value: complex) -> dict[str, float]:
    return {"real": value.real, "imag": value.imag}


def _deserialize_complex(data: dict[str, float]) -> complex:
    return complex(data["real"], data["imag"])


Serializable.register(complex, _serialize_complex, _deserialize_complex)


def check_serializable(serializable_object: Any) -> None:
    """Test if object is serializable and can be reconstructed from its serialization.

    Args:
        serializable_object: Object to be serialized and reconstructed.

    Raises:
        AssertionError: If the object is not Serializable, or if the reconstruction of
            the object is not equal to the original object.
    """
    # Test if object is Serializable
    assert isinstance(serializable_object, Serializable), "Object is not Serializable"  # noqa: S101
    # Test to and from JSON
    assert Serializable.from_json(serializable_object.to_json()) == serializable_object  # noqa: S101
    # Test to and from YAML
    assert Serializable.from_yaml(serializable_object.to_yaml()) == serializable_object  # noqa: S101

    with tempfile.TemporaryDirectory() as temp_dir:
        # Test to and from JSON file
        temp_file_path = Path(temp_dir) / "test_file.json"
        serializable_object.to_json_file(temp_file_path)
        assert Serializable.from_json_file(temp_file_path) == serializable_object  # noqa: S101

        # Test to and from YAML file
        temp_file_path = Path(temp_dir) / "test_file.yaml"
        serializable_object.to_yaml_file(temp_file_path)
        assert Serializable.from_yaml_file(temp_file_path) == serializable_object  # noqa: S101
