"""This module contains tests for ``tno.quantum.utils.validation``."""

from __future__ import annotations

import re
from datetime import timedelta
from numbers import Number
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes
from numpy.random import RandomState
from numpy.testing import assert_array_equal
from scipy.sparse import csr_array

from tno.quantum.utils.validation import (
    check_arraylike,
    check_ax,
    check_binary,
    check_bool,
    check_instance,
    check_int,
    check_kwarglike,
    check_path,
    check_python_variable,
    check_random_state,
    check_real,
    check_snake_case,
    check_string,
    check_timedelta,
    warn_if_negative,
    warn_if_positive,
)

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


class TestCheckReal:
    @pytest.mark.parametrize(
        ("arg", "expected_output"),
        [(0.0, 0.0), (float("inf"), float("inf")), (1, 1.0)],
        ids=["float_0", "float_inf", "int_1"],
    )
    def test_no_bounds(self, arg: float, expected_output: float) -> None:
        output = check_real(arg, "test")
        assert isinstance(output, float)
        assert output == expected_output

    def test_no_bounds_error(self) -> None:
        msg = "'test' should be a real number, but was of type <class 'complex'>"
        with pytest.raises(TypeError, match=msg):
            check_real(1 + 1j, "test")

    def test_l_bound(self) -> None:
        assert check_real(0, "test", l_bound=0) == 0
        assert check_real(-0, "test", l_bound=0) == 0

        msg = "'test' has an exclusive lower bound of 0.0, but was 0."
        with pytest.raises(ValueError, match=msg):
            check_real(0, "test", l_bound=0, l_inclusive=False)

        msg = "'test' has an inclusive lower bound of 0.0, but was -0.1."
        with pytest.raises(ValueError, match=msg):
            check_real(-0.1, "test", l_bound=0)

    def test_u_bound(self) -> None:
        assert check_real(0, "test", u_bound=0) == 0
        assert check_real(-0, "test", u_bound=0) == 0

        msg = "'test' has an exclusive upper bound of 0.0, but was 0."
        with pytest.raises(ValueError, match=msg):
            check_real(0, "test", u_bound=0, u_inclusive=False)

        msg = "'test' has an inclusive upper bound of 0.0, but was 0.1."
        with pytest.raises(ValueError, match=msg):
            check_real(0.1, "test", u_bound=0)


class TestCheckInt:
    def test_no_bounds(self) -> None:
        assert check_int(-1, "test") == -1
        assert check_int(1.0, "test") == 1

        msg = "'test' should be an integer, but was of type <class 'complex'>"
        with pytest.raises(TypeError, match=msg):
            check_int(1 + 1j, "test")

        msg = "'test' with value 1.1 could not be safely converted to an integer"
        with pytest.raises(ValueError, match=msg):
            check_int(1.1, "test")

    def test_l_bound(self) -> None:
        assert check_int(0, "test", l_bound=0) == 0
        assert check_int(-0, "test", l_bound=0) == 0

        msg = "'test' has an exclusive lower bound of 0.0, but was 0."
        with pytest.raises(ValueError, match=msg):
            check_int(0, "test", l_bound=0, l_inclusive=False)

        msg = "'test' has an inclusive lower bound of 0.0, but was -1."
        with pytest.raises(ValueError, match=msg):
            check_int(-1, "test", l_bound=0)

    def test_u_bound(self) -> None:
        assert check_int(0, "test", u_bound=0) == 0
        assert check_int(-0, "test", u_bound=0) == 0

        msg = "'test' has an exclusive upper bound of 0.0, but was 0."
        with pytest.raises(ValueError, match=msg):
            check_int(0, "test", u_bound=0, u_inclusive=False)

        msg = "'test' has an inclusive upper bound of 0.0, but was 1."
        with pytest.raises(ValueError, match=msg):
            check_int(1, "test", u_bound=0)


class TestCheckString:
    def test_no_keywords(self) -> None:
        assert check_string("Test", "test") == "Test"

    def test_lower(self) -> None:
        assert check_string("Test", "test", lower=True) == "test"

    def test_upper(self) -> None:
        assert check_string("Test", "test", upper=True) == "TEST"

    def test_error(self) -> None:
        msg = "'test' must be a string, but was of type <class 'int'>"
        with pytest.raises(TypeError, match=msg):
            check_string(1, "test")


class TestCheckPath:
    def test_valid_path(self, tmp_path: Path) -> None:
        valid_path = tmp_path / "valid_file.txt"
        valid_path.touch()
        assert check_path(valid_path, "test", must_exist=True) == valid_path
        assert check_path(valid_path, "test", must_be_file=True) == valid_path

    def test_valid_path_str(self) -> None:
        assert check_path("valid_path_string.py", "test", must_exist=False)

    def test_path_does_not_exist(self) -> None:
        path = Path("/invalid/path")
        msg = f"The path `{path}` does not exist."
        with pytest.raises(OSError, match=re.escape(msg)):
            check_path(path, "test", must_exist=True)

    def test_not_a_file(self, tmp_path: Path) -> None:
        valid_dir = tmp_path / "valid_directory"
        valid_dir.mkdir()
        msg = f"The path `{valid_dir}` is not a file."
        with pytest.raises(FileNotFoundError, match=re.escape(msg)):
            check_path(valid_dir, "test", must_be_file=True)

    def test_not_a_directory(self, tmp_path: Path) -> None:
        valid_file = tmp_path / "valid_file.txt"
        valid_file.touch()
        msg = f"The path `{valid_file}` is not a directory."
        with pytest.raises(NotADirectoryError, match=re.escape(msg)):
            check_path(valid_file, "test", must_be_dir=True)

    def test_invalid_type(self) -> None:
        msg = (
            "'test' should be a string or os.PathLike object, "
            "but was of type <class 'int'>"
        )
        with pytest.raises(TypeError, match=msg):
            check_path(123, "test")

    def test_suffix_path(self, tmp_path: Path) -> None:
        valid_path = tmp_path / "valid_file.txt"
        required_suffix = ".txt"
        valid_path.touch()
        assert (
            check_path(valid_path, "test", required_suffix=required_suffix)
            == valid_path
        )
        assert (
            check_path(
                tmp_path / "valid_file",
                "test",
                required_suffix=required_suffix,
            )
            == valid_path
        )
        assert (
            check_path(
                tmp_path / "valid_file.json",
                "test",
                required_suffix=required_suffix,
            )
            == valid_path
        )

    def test_suffix_path_safe(self) -> None:
        path = "valid_file.json"
        required_suffix = ".txt"
        error_msg = (
            f"The path `{path}` does not have the required suffix `{required_suffix}`."
        )
        with pytest.raises(ValueError, match=error_msg):
            check_path(
                path,
                "test",
                must_exist=False,
                required_suffix=required_suffix,
                safe=True,
            )


class TestCheckTimedelta:
    def test_valid_timedelta(self) -> None:
        assert check_timedelta(timedelta(seconds=10), "test") == timedelta(seconds=10)

    def test_valid_real(self) -> None:
        assert check_timedelta(10, "test") == timedelta(seconds=10)
        assert check_timedelta(10.4, "test") == timedelta(seconds=10.4)

    def test_invalid_type(self) -> None:
        msg = "'test' should be a real or a timedelta, but was of type <class 'str'>."
        with pytest.raises(TypeError, match=msg):
            check_timedelta("invalid", "test")

    def test_lower_bound_inclusive(self) -> None:
        l_bound = 10
        l_bound_time_delta = timedelta(seconds=l_bound)
        assert check_timedelta(l_bound, "test", l_bound=l_bound) == l_bound_time_delta
        assert (
            check_timedelta(l_bound, "test", l_bound=timedelta(seconds=l_bound))
            == l_bound_time_delta
        )

    def test_lower_bound_exclusive(self) -> None:
        msg = "'test' has an exclusive lower bound of 0:00:10, but was 0:00:10."
        with pytest.raises(ValueError, match=msg):
            check_timedelta(10, "test", l_bound=10, l_inclusive=False)

    def test_upper_bound_inclusive(self) -> None:
        u_bound = 10
        u_bound_time_delta = timedelta(seconds=u_bound)
        assert check_timedelta(u_bound, "test", u_bound=u_bound) == u_bound_time_delta
        assert (
            check_timedelta(u_bound, "test", u_bound=u_bound_time_delta)
            == u_bound_time_delta
        )

    def test_upper_bound_exclusive(self) -> None:
        msg = "'test' has an exclusive upper bound of 0:00:10, but was 0:00:10."
        with pytest.raises(ValueError, match=msg):
            check_timedelta(10, "test", u_bound=10, u_inclusive=False)

    def test_outside_bounds(self) -> None:
        msg = "'test' has an inclusive lower bound of 0:00:05, but was 0:00:04."
        with pytest.raises(ValueError, match=msg):
            check_timedelta(4, "test", l_bound=5)

        msg = "'test' has an inclusive upper bound of 0:00:05, but was 0:00:06."
        with pytest.raises(ValueError, match=msg):
            check_timedelta(6, "test", u_bound=5)


class TestCheckSnakeCaseConvention:
    @pytest.mark.parametrize(
        "x",
        ["valid", "valid_snake_case", "another_example", "variable_with_numbers123"],
    )
    def test_valid_snake_case_convention(self, x: str) -> None:
        assert check_snake_case(x, "test") == x

    @pytest.mark.parametrize(
        "x",
        [
            "camelCase",
            "PascalCase",
            "kebab-case",
            "UPPERCASE",
            "mixedCase123",
            "with spaces",
            "with-dashes",
            "1variable",
            "snake_case.variable1",
            "snake_case.1variable1",
        ],
    )
    def test_invalid_snake_case_convention(self, x: str) -> None:
        error_msg = f"'test' must be in snake case convention, but was '{x}'"
        with pytest.raises(ValueError, match=error_msg):
            check_snake_case(x, "test")

    @pytest.mark.parametrize(
        "x",
        ["valid.variable", "valid_snake.case", "another.example_with_numbers123"],
    )
    def test_valid_path(self, x: str) -> None:
        assert check_snake_case(x, "test", path=True) == x

    @pytest.mark.parametrize(
        "x",
        ["valid..variable", "valid_snake_case.camelCase", "example.1path"],
    )
    def test_invalid_path(self, x: str) -> None:
        error_msg = f"'test' must be in snake case convention, but was '{x}'"
        with pytest.raises(ValueError, match=error_msg):
            check_snake_case(x, "test", path=False)

    def test_error_string(self) -> None:
        msg = "'test' must be a string, but was of type <class 'int'>"
        with pytest.raises(TypeError, match=msg):
            check_snake_case(1, "test")

    def test_warn(self) -> None:
        x = "camelCase"
        msg = f"'test' is not in snake case convention, but was {x}."
        with pytest.warns(UserWarning, match=msg):
            check_snake_case(x, "test", warn=True)


class TestCheckPythonVariableConvention:
    @pytest.mark.parametrize(
        "x",
        [
            "variable_with_num123",
            "valid_variable",
            "camelCase",
            "PascalCase",
        ],
    )
    def test_valid_python_variable_convention(self, x: str) -> None:
        assert check_python_variable(x, "test") == x

    @pytest.mark.parametrize(
        "x",
        [
            "2invalidName",  # Starts with a digit
            "invalid-name",  # Contains a hyphen
            "inva!idvarab",  # Starts with a special character
            "invalid name",  # Contains a space
            "invalid$name",  # Contains a special character
            "kebab-varabl",  # kebab case
        ],
    )
    def test_invalid_python_variable_convention(self, x: str) -> None:
        error_msg = f"'test' must be in Python variable convention, but was '{x}'"
        with pytest.raises(ValueError, match=re.escape(error_msg)):
            check_python_variable(x, "test")

    def test_error_string(self) -> None:
        msg = "'test' must be a string, but was of type <class 'int'>"
        with pytest.raises(TypeError, match=msg):
            check_python_variable(1, "test")

    def test_warn(self) -> None:
        x = "123-variable"
        msg = f"'test' is not in Python variable convention, but was {x}."
        with pytest.warns(UserWarning, match=msg):
            check_python_variable(x, "test", warn=True)


class TestCheckBinary:
    def test_string(self) -> None:
        assert check_binary("1", "test") == 1
        assert check_binary("0", "test") == 0

    def test_int(self) -> None:
        assert check_binary(1, "test") == 1
        assert check_binary(0, "test") == 0

    def test_error(self) -> None:
        msg = "'test' must be a Binary variable, but was of type <class 'str'>"
        with pytest.raises(TypeError, match=msg):
            check_binary("2", "test")

        msg = "'test' has an inclusive upper bound of 1.0, but was 2"
        with pytest.raises(ValueError, match=msg):
            check_binary(2, "test")

        msg = "'test' has an inclusive lower bound of 0.0, but was -3"
        with pytest.raises(ValueError, match=msg):
            check_binary(-3, "test")

        msg = "'test' with value 2.1 could not be safely converted to an integer"
        with pytest.raises(ValueError, match=msg):
            check_binary(2.1, "test")


class TestCheckBool:
    def test_default(self) -> None:
        assert check_bool(True, "test")
        assert not check_bool(False, "test")

    def test_safe_is_false(self) -> None:
        assert check_bool(1, "test", safe=False)
        assert not check_bool(0, "test", safe=False)

    def test_safe_is_true(self) -> None:
        assert check_bool(True, "test", safe=True)
        with pytest.raises(TypeError):
            check_bool(0, "test", safe=True)


class TestArrayLike:
    @pytest.mark.parametrize(
        "arg",
        [np.zeros((2, 2)), [[0, 0], [0, 0]], ((0, 0), (0, 0)), csr_array((2, 2))],
        ids=["ndarray", "nested_list", "nested_tuple", "sparse_matrix"],
    )
    def test_input(self, arg: ArrayLike) -> None:
        assert_array_equal(check_arraylike(arg, "test", ndim=2), np.zeros((2, 2)))
        assert_array_equal(check_arraylike(arg, "test"), np.zeros((2, 2)))

    @pytest.mark.parametrize("arg", [np.zeros(2), None], ids=["1d", "None"])
    def test_error_n_dim(self, arg: Any) -> None:
        array = np.asarray(arg)
        msg = "'test' must be an ArrayLike with 2 dimension(s), but had "
        msg += f"{array.ndim} dimension(s)."
        with pytest.raises(ValueError, match=re.escape(msg)):
            check_arraylike(arg, "test", ndim=2)

    @pytest.mark.parametrize(
        ("test_array", "expected"),
        [
            (np.array([1, 2, 3]), np.array([1, 2, 3])),
            (np.array([1, 2, 3]).reshape((3, 1)), np.array([1, 2, 3])),
            (np.array([1, 2, 3]).reshape((1, 3)), np.array([1, 2, 3])),
            (np.array([[1, 2, 3]]), np.array([1, 2, 3])),
            (np.array([]), np.array([])),
            ([], np.array([])),
        ],
    )
    def test_1d_arraylike(
        self, test_array: ArrayLike, expected: NDArray[np.uint64]
    ) -> None:
        """Test special edge cases of ndim=1."""
        assert_array_equal(check_arraylike(test_array, "test", ndim=1), expected)

    @pytest.mark.parametrize(
        ("array", "ndim", "shape", "expected"),
        [
            (np.array([1, 2, 3]), 1, (3,), np.array([1, 2, 3])),
            (np.array([[1], [2], [3]]), 2, (3, 1), np.array([[1], [2], [3]])),
            (np.array([[1], [2], [3]]), 1, (3,), np.array([1, 2, 3])),
            (np.array([[1, 2, 3]]), 2, (1, 3), np.array([[1, 2, 3]])),
            (np.array([[1, 2, 3]]), 1, (3,), np.array([1, 2, 3])),
            (np.array([]), None, (0,), np.array([])),
            ([], None, (0,), np.array([])),
            (
                np.array([[1, 2, 3], [4, 5, 6]]),
                None,
                (2, 3),
                np.array([[1, 2, 3], [4, 5, 6]]),
            ),
        ],
    )
    def test_shape(
        self,
        array: ArrayLike,
        ndim: int | None,
        shape: tuple[int, ...],
        expected: NDArray[np.uint64],
    ) -> None:
        assert_array_equal(
            check_arraylike(array, "test", ndim=ndim, shape=shape), expected
        )

    @pytest.mark.parametrize(
        ("array", "ndim", "shape"),
        [
            (np.array([1, 2, 3]), None, (4,)),
            (np.array([1]), None, (1, 1)),
            (np.array([[1], [2], [3]]), None, (3,)),
            (np.array([[1], [2], [3]]), 1, (3, 1)),
        ],
    )
    def test_shape_error(
        self, array: ArrayLike, ndim: int | None, shape: tuple[int, ...]
    ) -> None:
        with pytest.raises(ValueError, match="shape"):
            check_arraylike(array, "test", ndim=ndim, shape=shape)


class TestCheckKwarglike:
    def test_default(self) -> None:
        assert check_kwarglike({"1": 2}, "test") == {"1": 2}

    def test_unsafe(self) -> None:
        input_kwarglike = {"1": [1]}
        output = check_kwarglike(input_kwarglike, "test")
        assert output["1"] is input_kwarglike["1"]

    def test_safe(self) -> None:
        input_kwarglike = {"1": [1]}
        output = check_kwarglike(input_kwarglike, "test", safe=True)
        assert output == input_kwarglike
        assert output["1"] is not input_kwarglike["1"]

    def test_type_error(self) -> None:
        msg = "'test' must be an instance of <class 'Mapping'>, "
        msg += "but was of type <class 'set'>"
        with pytest.raises(TypeError, match=msg):
            check_kwarglike({"1", 2}, "test")

    def test_key_error(self) -> None:
        msg = "At least one key in 'test' is not a string"
        with pytest.raises(KeyError, match=msg):
            check_kwarglike({"1": 2, 3: 4}, "test")


class TestCheckInstance:
    def test_default(self) -> None:
        check_instance(1, "test", int)
        check_instance(1, "test", Number)
        check_instance("TEST", "test", str)

    def test_error(self) -> None:
        msg = (
            "'test' must be an instance of <class 'str'>, but was of type <class 'int'>"
        )
        with pytest.raises(TypeError, match=msg):
            check_instance(1, "test", str)


class TestCheckRandomState:
    def test_default(self) -> None:
        """Test if check_random_state does not fail on good input."""
        check_random_state(None, "random_state")
        check_random_state(RandomState(), "random_state")
        check_random_state(123, "random_state")

    def test_error(self) -> None:
        """Test if check_random_state raises error on bad input."""
        with pytest.raises(TypeError, match="'random_state' should be"):
            check_random_state("bad input", "random_state")

    def test_seed(self) -> None:
        """Test if same seed produces the same random state."""
        a = check_random_state(42, "random_state")
        b = check_random_state(RandomState(42), "random_state")
        c = check_random_state(100, "random_state")
        x, y, z = a.rand(), b.rand(), c.rand()
        assert x == y
        assert x != z


class TestParseAx:
    def test_default(self) -> None:
        axes = check_ax(None, "axes")
        assert isinstance(axes, Axes)

    def test_axes(self) -> None:
        _, axes = plt.subplots()
        assert axes is check_ax(axes, "axes")

    def test_error(self) -> None:
        msg = "'test' should be a `Axes` or `None`, but was of type <class 'str'>."
        with pytest.raises(TypeError, match=msg):
            check_ax("test", "test")


def test_warn_if_positive() -> None:
    warn_if_positive(0, "test")
    warn_if_positive(-1.0, "test")

    with pytest.warns(UserWarning, match="was positive") as record:
        warn_if_positive(1, "test")

    assert len(record) == 1
    assert isinstance(record[0].message, Warning)
    assert record[0].message.args[0] == "'test' was positive"


def test_warn_if_negative() -> None:
    warn_if_negative(0, "test")
    warn_if_negative(1.0, "test")

    with pytest.warns(UserWarning, match="was negative") as record:
        warn_if_negative(-1, "test")

    assert len(record) == 1
    assert isinstance(record[0].message, Warning)
    assert record[0].message.args[0] == "'test' was negative"
