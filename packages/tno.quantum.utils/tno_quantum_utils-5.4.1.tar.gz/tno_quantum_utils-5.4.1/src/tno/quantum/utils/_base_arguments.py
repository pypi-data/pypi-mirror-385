"""This module contains the ``BaseArguments`` class."""

from __future__ import annotations

import warnings
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, fields
from inspect import Parameter
from typing import TYPE_CHECKING, Any

from tno.quantum.utils._utils import get_init_arguments_info
from tno.quantum.utils.serialization import Serializable

if TYPE_CHECKING:
    from typing import Self


@dataclass
class BaseArguments(Mapping[str, Any], Serializable):
    r'''Base class for argument classes.

    Example:
        >>> from dataclasses import dataclass
        >>> from tno.quantum.utils import BaseArguments
        >>>
        >>> @dataclass
        ... class ExampleArguments(BaseArguments):
        ...     """
        ...     Attributes:
        ...         name: attribute description name
        ...         size: attribute description size
        ...     """
        ...     name: str = "test-name"
        ...     size: int = 5
        >>>
        >>> args = ExampleArguments.from_mapping({ "name": "example", "size": 42 })
        >>> args.name
        'example'
    '''

    def __getitem__(self, key: str) -> Any:
        """Retrieve attribute item by key.

        Args:
            key: Key to retrieve.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key is not found.
        """
        if hasattr(self, key):
            return getattr(self, key)
        error_msg = f"`{key}` not found in Arguments."
        raise KeyError(error_msg)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the keys in the instance corresponding to known attributes."""
        return iter(field.name for field in fields(self))

    def __len__(self) -> int:
        """Return the number of known attribute keys."""
        return len(fields(self))

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Self:
        """Create an instance from a mapping.

        Args:
            data: Mapping containing key-value pairs to store in an arguments object.
                keys that are not recognized as attributes will be ignored. If a known
                argument is missing but has a default value, default value will be used.

        Returns:
            Instance of arguments.

        Raises:
            KeyError: If the data does not contain all the attribute keys for which no
                default value is known.
            UserWarning: If data contains keys that are not recognized as attributes.
        """
        if isinstance(data, cls):
            return data

        init_args_info = get_init_arguments_info(cls)
        extra_args = set(data.keys()) - set(init_args_info.keys())
        if extra_args:
            warnings.warn(
                f"Ignoring unknown keys: {', '.join(extra_args)}",
                UserWarning,
                stacklevel=2,
            )

        args: dict[str, Any] = {
            arg_name: arg_value
            for arg_name, arg_value in data.items()
            if arg_name in init_args_info
        }

        # Check missing required arguments
        for arg_name, default_value in init_args_info.items():
            if arg_name not in data and default_value is Parameter.empty:
                error_msg = f"Missing required key: {arg_name}"
                raise KeyError(error_msg)

        return cls(**args)
