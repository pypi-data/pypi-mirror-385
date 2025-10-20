"""This module contains utility functions."""

import importlib.util
import inspect
import re
from typing import Any

from tno.quantum.utils.validation import check_string

if importlib.util.find_spec("numpy") is not None:
    import numpy as np


def convert_to_snake_case(x: str, *, path: bool = False) -> str:
    """Convert string to snake case.

    Args:
        x: String to convert.
        path: If ``True``, treats the variable as a path variable with periods. Each
            substring separated by a period will be converted to a valid snake case
            convention. Defaults to ``False``.

    Raises:
        TypeError: If `x` is not an instance of :py:const:`str`.
        ValueError: If the input cannot be converted to snake case because it starts
            with an invalid character (anything other than a letter).

    Returns:
        Snake case variant of `x`.
    """
    x = check_string(x, "x")

    if path:
        substrings = [
            convert_to_snake_case(substring, path=False) for substring in x.split(".")
        ]
        return ".".join(substrings).lower()

    if not re.match(r"^[a-zA-Z]", x):
        error_msg = "Input cannot start with a number or any special symbol."
        raise ValueError(error_msg)

    if re.search(r"[^a-zA-Z0-9 \-_]", x):
        error_msg = "Input cannot contain special characters."
        raise ValueError(error_msg)

    # Convert x to snake_case convention
    words = x.replace("-", " ").split()
    words = [re.sub(r"([A-Z]+)", r" \1", word) for word in words]
    words = [re.sub(r"([A-Z][a-z]+)", r" \1", word) for word in words]
    words = [word.strip() for word in words]
    return "_".join(words).replace(" ", "_").replace("__", "_").lower()


def get_installed_subclasses(module_name: str, subclass: Any) -> dict[str, type[Any]]:
    """Obtain all installed subclasses within a module.

    Args:
        module_name: Name of the module to search.
        subclass: The subclass to search for.

    Returns:
        Dictionary with subclasses by their snake-case name.
    """
    supported_subclasses = {}

    module = importlib.import_module(module_name)
    for name in dir(module):
        obj = getattr(module, name)

        # Determine if object is subclass of the to search for class.
        if inspect.isclass(obj):
            mro = inspect.getmro(obj)
        else:
            mro = inspect.getmro(obj.__class__)
        if any(issubclass(cls, subclass) for cls in mro):
            supported_subclasses[convert_to_snake_case(name)] = obj

    return supported_subclasses


def get_init_arguments_info(cls: type[Any]) -> dict[str, Any]:
    """Retrieve names, and default values of ``__init__`` arguments for a given class.

    Args:
        cls: The class to inspect.

    Returns:
        A dictionary where the keys are argument names and the values are the parameter
        default values (if any, otherwise ``Parameter.empty``).
    """
    init_signature = inspect.signature(cls.__init__)
    init_args = {}
    for param in init_signature.parameters.values():
        if param.name == "self":
            continue
        init_args[param.name] = param.default
    return init_args


def check_equal(first: Any, second: Any) -> bool:  # noqa: PLR0911
    """Check if two objects are equal.

    Equality check if applied recursively on lists, tuples, dictionaries and NumPy
    arrays. That is, such objects are considered equal if all their elements are equal.

    Args:
        first: First object to compare.
        second: Second object to compare.

    Returns:
        True if objects are equal, otherwise false.
    """
    if type(first) is not type(second):
        return False

    if isinstance(first, dict):
        if len(first) != len(second):
            return False
        for key in first:
            if key not in second:
                return False
            if not check_equal(first[key], second[key]):
                return False
        return True

    if isinstance(first, (list, tuple)):
        if len(first) != len(second):
            return False
        return all(check_equal(x, y) for x, y in zip(first, second, strict=True))

    if importlib.util.find_spec("numpy") is not None and isinstance(first, np.ndarray):
        return np.array_equal(first, second)

    return bool(first == second)
