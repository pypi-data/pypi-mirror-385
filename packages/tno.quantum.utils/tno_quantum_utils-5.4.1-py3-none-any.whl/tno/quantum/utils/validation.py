"""This module contains generic validation methods."""

from __future__ import annotations

import importlib.util
import os
import re
import warnings
from collections.abc import Mapping
from copy import deepcopy
from datetime import timedelta
from numbers import Integral, Real
from pathlib import Path
from typing import TYPE_CHECKING, Any, SupportsFloat, TypeVar

import numpy as np
from numpy.random import RandomState
from numpy.typing import NDArray

TYPE_BOUNDS = TypeVar("TYPE_BOUNDS", float, int, timedelta)
TYPE_INSTANCE = TypeVar("TYPE_INSTANCE")

if TYPE_CHECKING:
    from numpy.typing import NDArray

# ruff: noqa:  PLR0913


def check_real(
    x: Any,
    name: str,
    *,
    l_bound: SupportsFloat | None = None,
    u_bound: SupportsFloat | None = None,
    l_inclusive: bool = True,
    u_inclusive: bool = True,
) -> float:
    """Check if the variable `x` with name `name` is a real number.

    Optionally, lower and upper bounds can also be checked.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        l_bound: Lower bound of `x`.
        u_bound: Upper bound of `x`.
        l_inclusive: If ``True`` the lower bound is inclusive, otherwise the lower bound
            is exclusive.
        u_inclusive: If ``True`` the upper bound is inclusive, otherwise the upper bound
            is exclusive.

    Raises:
        TypeError: If `x` is not a real number.
        ValueError: If `x` is outside the give bounds.

    Returns:
        Floating point representation of `x`.
    """
    if not isinstance(x, Real):
        error_msg = f"'{name}' should be a real number, but was of type {type(x)}."
        raise TypeError(error_msg)

    x_float = float(x)
    if l_bound is not None:
        check_lower_bound(x_float, name, float(l_bound), inclusive=l_inclusive)

    if u_bound is not None:
        check_upper_bound(x_float, name, float(u_bound), inclusive=u_inclusive)

    return x_float


def check_int(
    x: Any,
    name: str,
    *,
    l_bound: SupportsFloat | None = None,
    u_bound: SupportsFloat | None = None,
    l_inclusive: bool = True,
    u_inclusive: bool = True,
) -> int:
    """Check if the variable `x` with name `name` is an integer.

    Optionally, lower and upper bounds can also be checked.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        l_bound: Lower bound of `x`.
        u_bound: Upper bound of `x`.
        l_inclusive: If ``True`` the lower bound is inclusive, otherwise the lower
            bound is exclusive.
        u_inclusive: If ``True`` the upper bound is inclusive, otherwise the upper
            bound is exclusive.

    Raises:
        TypeError: If `x` is not an integer.
        ValueError: If `x` is outside the give bounds.

    Returns:
        Integer representation of `x`.
    """
    if not isinstance(x, Real):
        error_msg = f"'{name}' should be an integer, but was of type {type(x)}"
        raise TypeError(error_msg)

    int_x: int = int(x)  # type: ignore[call-overload]
    if not isinstance(x, Integral) and x - int_x != 0:
        msg = f"'{name}' with value {x} could not be safely converted to an integer"
        raise ValueError(msg)

    if l_bound is not None:
        check_lower_bound(int_x, name, float(l_bound), inclusive=l_inclusive)

    if u_bound is not None:
        check_upper_bound(int_x, name, float(u_bound), inclusive=u_inclusive)

    return int_x


def check_lower_bound(
    x: TYPE_BOUNDS, name: str, l_bound: TYPE_BOUNDS, *, inclusive: bool
) -> None:
    """Check if the variable `x` with name `name` satisfies a lower bound.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        l_bound: Lower bound of `x`.
        inclusive: If ``True`` the lower bound is inclusive, otherwise the lower
            bound is exclusive.

    Raises:
        ValueError: If `x` is outside the give bounds.
    """
    error_msg = f"'{name}" + "' has an {} lower bound of {}" + f", but was {x!s}."
    if inclusive and x < l_bound:
        raise ValueError(error_msg.format("inclusive", l_bound))
    if not inclusive and x <= l_bound:
        raise ValueError(error_msg.format("exclusive", l_bound))


def check_upper_bound(
    x: TYPE_BOUNDS, name: str, u_bound: TYPE_BOUNDS, *, inclusive: bool
) -> None:
    """Check if the variable `x` with name `name` satisfies an upper bound.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        u_bound: Upper bound of `x`.
        inclusive: If ``True`` the lower bound is inclusive, otherwise the lower
            bound is exclusive.

    Raises:
        ValueError: If `x` is outside the give bounds.
    """
    error_msg = f"'{name}" + "' has an {} upper bound of {}" + f", but was {x!s}."
    if inclusive and x > u_bound:
        raise ValueError(error_msg.format("inclusive", u_bound))
    if not inclusive and x >= u_bound:
        raise ValueError(error_msg.format("exclusive", u_bound))


def check_string(
    x: Any,
    name: str,
    *,
    lower: bool = False,
    upper: bool = False,
) -> str:
    """Check if the variable `x` with name `name` is a string.

    Optionally, the string can be converted to all lowercase or all uppercase letters.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        lower: If ``True``, `x` will be returned with lowercase letters. Defaults to
            ``False``.
        upper: If ``True``, `x` will be returned with uppercase letters. Default to
            ``False``.

    Raises:
        TypeError: If `x` is not an instance of :py:const:`str`.

    Returns:
        Input string. Optionally, in lowercase or uppercase letters.
    """
    if not isinstance(x, str):
        error_msg = f"'{name}' must be a string, but was of type {type(x)}"
        raise TypeError(error_msg)

    if lower:
        return x.lower()
    if upper:
        return x.upper()

    return x


def check_snake_case(
    x: Any, name: str, *, path: bool = False, warn: bool = False
) -> str:
    """Check if the variable `x` with name `name` is a string in snake case convention.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        path: If ``True``, treats the name as a path variable with periods. Each
            substring separated by a period must be in valid snake case convention.
            Defaults to ``False``.
        warn: If ``True``, issue a warning instead of raising an ValueError.
            Defaults to ``False``

    Raises:
        TypeError: If `x` is not an instance of :py:const:`str`.
        ValueError: If `x` is not in snake case and `warn` is ``False``.

    Returns:
        Input string.
    """
    y = check_string(x, name)

    if path:  # allowing periods
        snake_case_pattern = re.compile(
            r"^[a-z][a-z0-9]*(_[a-z0-9]+|\.[a-z][a-z0-9]*)*$"
        )
    else:
        snake_case_pattern = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")

    if not snake_case_pattern.match(y):
        if warn:
            warn_msg = f"'{name}' is not in snake case convention, but was {y}."
            warnings.warn(warn_msg, stacklevel=2)
        else:
            error_msg = f"'{name}' must be in snake case convention, but was '{y}'"
            raise ValueError(error_msg)
    return y


def check_python_variable(x: Any, name: str, *, warn: bool = False) -> str:
    """Check if variable `x` with name `name` is a string in Python variable convention.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        warn: If ``True``, issue a warning instead of raising an ValueError.
            Defaults to ``False``
    Raises:
        TypeError: If `x` is not an instance of :py:const:`str`.
        ValueError: If `x` is not in Python variable convention and `warn` is ``False``.

    Returns:
        Input string.
    """
    y = check_string(x, name)

    python_variable_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    if not python_variable_pattern.match(y):
        if warn:
            warn_msg = f"'{name}' is not in Python variable convention, but was {y}."
            warnings.warn(warn_msg, stacklevel=2)
        else:
            error_msg = f"'{name}' must be in Python variable convention, but was '{y}'"
            raise ValueError(error_msg)
    return y


def check_bool(x: Any, name: str, *, safe: bool = False) -> bool:
    """Check if the variable `x` with name `name` is a boolean value.

    Optionally, cast to boolean value if it is not.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        safe: If ``True`` raise a `TypeError` when `x` is not a bool. If ``False``
            cast to bool.

    Raises:
        TypeError: If `safe` is ``True`` and `x` is not a boolean value.

    Returns:
        Boolean representation of the input.
    """
    if not isinstance(x, bool) and safe:
        error_msg = f"'{name}' must be a boolean value, but was of type {type(x)}"
        raise TypeError(error_msg)
    return bool(x)


def check_binary(x: Any, name: str) -> int:
    """Check if the variable `x` with name `name` is a binary variable.

    Will casts the variable to int representation.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.

    Raises:
        TypeError: If `x` is a string but does not have a binary value.
        ValueError: If `x` could not safely be converted to the integer 0 or 1.

    Returns:
        Binary int representation of the input.
    """
    if isinstance(x, str):
        if x in ("0", "1"):
            return int(x)
        msg = f"'{name}' must be a Binary variable, but was of type {type(x)}"
        raise TypeError(msg)

    return check_int(x, name, l_bound=0, u_bound=1)


def check_kwarglike(x: Any, name: str, *, safe: bool = False) -> dict[str, Any]:
    """Check if the variable `x` with name `name` is a kwarglike object.

    A object is kwarglike if it is a mapping where all keys are strings.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        safe: If ``True``, makes a deep copy of all values of `x`.

    Raises:
        TypeError: If `x` is not a Mapping.
        KeyError: If `x` has at least one key that is not a string.

    Returns:
        Dictionary with the key-value pairs from `x`.
    """
    if not isinstance(x, Mapping):
        error_msg = (
            f"'{name}' must be an instance of <class 'Mapping'>,"
            f" but was of type {type(x)}"
        )
        raise TypeError(error_msg)

    x_dict = {}
    for key, value in x.items():
        if not isinstance(key, str):
            error_msg = f"At least one key in '{name}' is not a string"
            raise KeyError(error_msg)
        x_dict[key] = deepcopy(value) if safe else value

    return x_dict


def check_arraylike(
    x: Any, name: str, *, ndim: int | None = None, shape: tuple[int, ...] | None = None
) -> NDArray[Any]:
    """Check if the variable `x` with name `name` is an ArrayLike.

    Optionally, check if the result has the specified number of dimensions.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        ndim: Number of dimensions `x` should have. When `ndim = 1`, arrays with more
            than one dimension will be squeezed to remove dimensions of size one.
        shape: Shape `x` should have.

    Raises:
        ValueError: When the provided input is not ArrayLike or does not have the
            correct shape or number of dimensions.

    Returns:
        NDArray representation of `x`.
    """
    array: NDArray[Any]
    array = x.toarray() if hasattr(x, "toarray") else np.asarray(x)

    if ndim is not None:
        if ndim == 1 and array.ndim != 1:
            array = array.squeeze()

        if array.ndim != ndim:
            msg = f"'{name}' must be an ArrayLike with {ndim} dimension(s), but had "
            msg += f"{array.ndim} dimension(s)."
            raise ValueError(msg)

    if shape is not None and array.shape != shape:
        msg = f"'{name}' must be an ArrayLike of shape {shape}, but had "
        msg += f"shape {array.shape}."
        raise ValueError(msg)

    return array


def check_instance(x: TYPE_INSTANCE, name: str, dtype: type) -> TYPE_INSTANCE:
    """Check if `x` with name `name` is an instance of dtype.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        dtype: the type of variable to validate against.

    Raises:
        TypeError: If `x` is not an instance of `dtype`.

    Returns:
        The input `x` if it is an instance of `dtype`.
    """
    if not isinstance(_ := x, dtype):  # `_ := x` instead of `x` to fix mypy
        msg = f"'{name}' must be an instance of {dtype}, but was of type {type(x)}"
        raise TypeError(msg)
    return x


def check_path(
    x: Any,
    name: str,
    *,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    required_suffix: str | None = None,
    safe: bool = False,
) -> Path:
    """Check if the variable `path` with name `name` is a valid path.

    Optionally, existence, file, and directory checks can also be performed.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        required_suffix: If specified, the path must have this suffix.
        must_exist: If ``True``, the path must exist.
        must_be_file: If ``True``, the path must be a file.
        must_be_dir: If ``True``, the path must be a directory.
        safe: If ``True`` and the path does not have the required suffix a
            ``ValueError`` is raised. Otherwise, if ``False``, the suffix  will be
            replaced to match the required_suffix.

    Raises:
        TypeError: If `path` is not a string or Path object.
        ValueError: If `path` does not have the correct required_suffix.
        OSError: If `path` does not exist while must_exist is ``True``
        FileNotFoundError: If `path` is not a file while must_be_file is ``True``
        NotADirectoryError: If `path` is not a directory while must_be_dir is ``True``

    Returns:
        Path object representing `path`.
    """
    if not isinstance(x, (str, os.PathLike)):
        error_msg = (
            f"'{name}' should be a string or os.PathLike object, "
            f"but was of type {type(x)}."
        )

        raise TypeError(error_msg)

    path_obj = Path(x)

    if required_suffix:
        if path_obj.suffix != required_suffix and safe:
            error_msg = (
                f"The path `{path_obj}` does not have the required suffix "
                f"`{required_suffix}`."
            )
            raise ValueError(error_msg)

        path_obj = path_obj.with_suffix(required_suffix)

    if must_exist and not path_obj.exists():
        error_msg = f"The path `{path_obj}` does not exist."
        raise OSError(error_msg)

    if must_be_file and not path_obj.is_file():
        error_msg = f"The path `{path_obj}` is not a file."
        raise FileNotFoundError(error_msg)

    if must_be_dir and not path_obj.is_dir():
        error_msg = f"The path `{path_obj}` is not a directory."
        raise NotADirectoryError(error_msg)

    return path_obj


def check_timedelta(
    x: Any,
    name: str,
    *,
    l_bound: SupportsFloat | timedelta | None = None,
    u_bound: SupportsFloat | timedelta | None = None,
    l_inclusive: bool = True,
    u_inclusive: bool = True,
) -> timedelta:
    """Check if the variable `x` with name `name` can be converted to a timedelta.

    Optionally, lower and upper bounds can also be checked.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.
        l_bound: Lower bound of `x`.
        u_bound: Upper bound of `x`.
        l_inclusive: If ``True`` the lower bound is inclusive, otherwise the lower bound
            is exclusive.
        u_inclusive: If ``True`` the upper bound is inclusive, otherwise the upper bound
            is exclusive.

    Raises:
        TypeError: If `x` cannot be converted to a timedelta.
        ValueError: If `x` is outside the given bounds.

    Returns:
        Timedelta representation of `x`.
    """
    if not isinstance(x, (Real, timedelta)):
        error_msg = (
            f"'{name}' should be a real or a timedelta, but was of type {type(x)}."
        )
        raise TypeError(error_msg)

    if isinstance(x, timedelta):
        td = x
    elif isinstance(x, Real):
        td = timedelta(seconds=float(x))

    if l_bound is not None:
        l_bound_ = check_timedelta(l_bound, name="l_bound")
        check_lower_bound(td, name, l_bound_, inclusive=l_inclusive)

    if u_bound is not None:
        u_bound_ = check_timedelta(u_bound, name="u_bound")
        check_upper_bound(td, name, u_bound_, inclusive=u_inclusive)

    return td


def check_random_state(
    x: Any,
    name: str,
) -> RandomState:
    """Check if the variable `x` with name `name` can be converted to a :py:class:`~numpy.random.RandomState`.

    If `x` is already a :py:class:`~numpy.random.RandomState` instance, return it.
    If `x` is an integer, return a new :py:class:`~numpy.random.RandomState` instance seeded with `x`.
    If `x` is ``None``, return a new unseeded :py:class:`~numpy.random.RandomState` instance.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in possible error
            messages.

    Raises:
        TypeError: If `x` is not an instance of ``None``, :py:class:`~numbers.Integral` or
            :py:class:`~numpy.random.RandomState`.
    """  # noqa: E501
    if x is None:
        return RandomState()
    if isinstance(x, Integral):
        return RandomState(int(x))
    if isinstance(x, RandomState):
        return x

    error_msg = (
        f"'{name}' should be a ``RandomState``, integer or ``None``, "
        f"but was of type {type(x)}."
    )
    raise TypeError(error_msg)


if importlib.util.find_spec("matplotlib") is not None:
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes

    def check_ax(
        x: Any,
        name: str,
    ) -> Axes:
        """Check if the variable `x` with name `name` can be converted to an :py:class:`~matplotlib.axes.Axes` object.

        If `x` is already a :py:class:`~matplotlib.axes.Axes` instance, return it.
        If `x` is ``None``, return a new :py:class:`~matplotlib.axes.Axes` instance.

        Args:
            x: Variable to check.
            name: Name of the variable. This name will be displayed in possible error
                messages.

        Returns:
            Parsed ax.

        Raises:
            TypeError: If `x` is not ``None`` or an instance of :py:class:`~matplotlib.axes.Axes`.
        """  # noqa: E501
        if isinstance(x, Axes):
            return x
        if x is None:
            _, ax = plt.subplots()
            return ax
        error_msg = f"'{name}' should be a `Axes` or `None`, but was of type {type(x)}."
        raise TypeError(error_msg)


def warn_if_positive(x: SupportsFloat, name: str) -> None:
    """Give a warning when `x` is positive.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in the warning.
    """
    if float(x) > 0:
        warn_msg = f"'{name}' was positive"
        warnings.warn(warn_msg, stacklevel=2)


def warn_if_negative(x: SupportsFloat, name: str) -> None:
    """Give a warning when `x` is negative.

    Args:
        x: Variable to check.
        name: Name of the variable. This name will be displayed in the warning.
    """
    if float(x) < 0:
        warn_message = f"'{name}' was negative"
        warnings.warn(warn_message, stacklevel=2)
