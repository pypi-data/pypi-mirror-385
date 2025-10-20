"""This module contains the ``BaseConfig`` class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from tno.quantum.utils._base_arguments import BaseArguments
from tno.quantum.utils._utils import convert_to_snake_case
from tno.quantum.utils.validation import (
    check_kwarglike,
    check_snake_case,
    check_string,
)

T = TypeVar("T")


@dataclass(init=False)
class BaseConfig(ABC, BaseArguments, Generic[T]):
    """Abstract base configuration class for creating instances of a specific class.

    The :py:class:`BaseConfig` class allows users to easily create configuration classes
    that can be used to instantiate arbitrary class objects. For instance, see
    :py:class:`~BackendConfig` or :py:class:`~OptimizerConfig`.

    Each configuration class must implement a :py:meth:`supported_items` method that
    returns a dictionary with as keys the `snake_case` class names and as values
    constructors of supported classes. These can be either the class or callable objects
    that return class instances.

    From a configuration object, instances can be created using the
    :py:meth:`get_instance` method.

    The `name` attribute can be provided in either snake_case, camelCase or PascalCase,
    that is, ``"TestSolver"`` and ``"test_solver"`` will be treated the same.

    Example:
        >>> from tno.quantum.utils import BaseConfig
        >>>
        >>> def add(x, y):
        ...     return x + y
        >>>
        >>> def mul(x, y):
        ...     return x * y
        >>>
        >>> class IntegerConfig(BaseConfig[int]):
        ...     @staticmethod
        ...     def supported_items():
        ...         return { "add": add, "mul": mul }
        >>>
        >>> config = IntegerConfig(name="mul", options={"x": 6, "y": 7})
        >>> config.get_instance()
        42
    """

    _name: str
    _options: dict[str, Any]
    _supported_custom_items: ClassVar[dict[str, type[Any] | Callable[..., Any]]] = {}

    def __init__(self, name: str, options: Mapping[str, Any] | None = None) -> None:
        """Init :py:class:`BaseConfig`.

        Args:
            name: Name used to determine the name of the to instantiate class.
            options: Keyword arguments to be passed to the constructor of the class.

        Raises:
            TypeError: If `name` is not a string or `options` is not a mapping.
            KeyError: If `options` has a key that is not a string.
            KeyError: If `name` does not match any of the supported items.
        """
        self._name = check_string(name, "name")
        self._name = convert_to_snake_case(self._name, path=True)
        self._options = (
            check_kwarglike(options, "options", safe=True)
            if options is not None
            else {}
        )

        if self._name not in self.supported_items() | self.supported_custom_items():
            msg = f"Name '{self._name}' does not match any of the supported items."
            raise KeyError(msg)

    @property
    def name(self) -> str:
        """Name used to determine the name of the to instantiate class."""
        return self._name

    @property
    def options(self) -> dict[str, Any]:
        """Keyword arguments to be passed to the constructor of the class."""
        return self._options

    @staticmethod
    @abstractmethod
    def supported_items() -> (
        dict[str, type[T]]
        | dict[str, Callable[..., T]]
        | dict[str, type[T] | Callable[..., T]]
    ):
        """Returns the supported classes.

        This method must be implemented for each configuration class and should return a
        dictionary with as keys the `snake_case` class names and values the supported
        classes or callable objects that return supported classes.

        Returns:
            Dictionary with constructors of supported classes.
        """

    @classmethod
    def supported_custom_items(
        cls,
    ) -> (
        dict[str, type[T]]
        | dict[str, Callable[..., T]]
        | dict[str, type[T] | Callable[..., T]]
    ):
        """Returns the supported custom classes."""
        prefix = cls.prefix()
        return {
            full_name[len(prefix) :]: item
            for full_name, item in cls._supported_custom_items.items()
            if full_name.startswith(prefix)
        }

    @classmethod
    def register_custom_item(cls, name: str, item: type[T] | Callable[..., T]) -> None:
        """Register a custom item to the supported custom items.

        Args:
            name: Name of the custom item to be added. Will be converted to
                snake_case version.
            item: Custom item to be added. Item needs to be a constructor of the
                custom class and can be the class itself or a callable function that
                returns the class instance.

        Raises:
            ValueError: If `name` already exists in supported items or supported
                custom items.
            TypeError: If `item` is not a class or callable object.
        """
        check_snake_case(name, "name", path=True, warn=True)
        name = convert_to_snake_case(name, path=True)

        if not callable(item):
            msg = f"Provided item {item} is not a class or callable object."
            raise TypeError(msg)

        if name in cls.supported_items():
            msg = (
                f"The custom item with name `{name}` can't be added because there "
                f"already exists a similar named item within `supported_items`."
            )
            raise ValueError(msg)

        if name in cls.supported_custom_items():
            msg = (
                f"The custom item with name `{name}` can't be added because there "
                f"already exists a similar named item within `supported_custom_items`."
            )
            raise ValueError(msg)

        cls._supported_custom_items[cls.prefix() + name] = item

    @classmethod
    def prefix(cls) -> str:
        """Compute prefix that prevents naming conflicts in storage of custom items."""
        return f"{cls.__name__}-"

    def get_constructor(self) -> type[T] | Callable[..., T]:
        """Get the object constructor.

        Returns:
            A constructor that can create class instance of the configured object.

        Raises:
            KeyError: If the configuration is not among supported items.
        """
        supported_items = self.supported_items()
        supported_custom_items = self.supported_custom_items()
        all_supported_items: dict[str, type[T] | Callable[..., T]] = {
            **supported_items,
            **supported_custom_items,
        }

        name_snake_case = convert_to_snake_case(self._name, path=True)
        if name_snake_case not in all_supported_items:
            msg = (
                f"The provided configuration with name `{self._name}` is invalid. "
                f"Allowed values are: {list(all_supported_items.keys())}."
            )
            raise KeyError(msg)
        return all_supported_items[name_snake_case]

    def get_instance(self, *additional_args: Any, **additional_kwargs: Any) -> T:
        """Creates configured object instance.

        Args:
            additional_args: Additional constructor arguments to be passed to the class.
            additional_kwargs: Additional constructor keyword arguments that are not
                provided by the options, If the keyword argument is also provided in the
                options, the``additional_kwargs`` take priority.

        Returns:
            A configured object.
        """
        object_class = self.get_constructor()
        return object_class(*additional_args, **{**self._options, **additional_kwargs})
