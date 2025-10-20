"""This module contains tests for ``BitVector``."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import numpy as np
import pytest

if TYPE_CHECKING:
    from numpy.typing import NDArray

from tno.quantum.utils import BitVector, BitVectorLike
from tno.quantum.utils.serialization import check_serializable


@pytest.fixture(name="input_array")
def input_array_fixture() -> NDArray[Any]:
    """NP array fixture."""
    return np.array([0, 1, 0, 1])


@pytest.fixture(name="input_dict")
def input_dict_fixture() -> dict[str, int]:
    """Dictionary fixture."""
    return {"a": 1, "b": 0, "c": 1, "d": 0}


@pytest.mark.parametrize(
    ("input_data", "expected_output"),
    [
        ("0101", np.array([0, 1, 0, 1])),
        ([0, 1, 1, 0], np.array([0, 1, 1, 0])),
        (np.array([1, 0, 1, 1]), np.array([1, 0, 1, 1])),
        ([True, True, False], np.array([1, 1, 0])),
        ({"1": 0, "2": 1}, np.array([0, 1])),
        ({"x[1]": 0, "x[0]": 1}, np.array([0, 1])),
        ({"bb": 0, "aa": 1}, np.array([0, 1])),
    ],
)
def test_binary_vector_correct_inputs(
    input_data: BitVectorLike,
    expected_output: NDArray[Any],
) -> None:
    """Test `BitVector` with correct inputs."""
    bits = BitVector(input_data).bits
    np.testing.assert_array_equal(bits, expected_output)


def test_binary_vector_indexing() -> None:
    """Test indexing of BitVector."""
    bit_string = "11001100"
    bit_vector = BitVector(bit_string)
    for i, str_val in enumerate(bit_string):
        assert int(str_val) == bit_vector[i]


@pytest.mark.parametrize(
    ("input_data", "expected_error_type"),
    [
        ("0a1b0c1!", "invalid_input_str"),
        ("012", "invalid_input_str"),
        ({"1": "2"}, "invalid_input_upper"),
        ({0: "a"}, "invalid_input_type"),
        ({"1": 3}, "invalid_input_upper"),
        ({"1": -2}, "invalid_input_lower"),
        ({0, 1}, "invalid_input_type"),
        (np.ones(shape=(3, 3)), "invalid_input_type"),
    ],
)
def test_binary_vector_invalid_inputs(
    input_data: Any, expected_error_type: str
) -> None:
    """Test BitVector with invalid inputs."""

    error_msgs = {
        "invalid_input_str": (TypeError, "must be a Binary variable, but was of type"),
        "invalid_input_type": (
            TypeError,
            "The provided input `bits` must be a str, "
            "Mapping[Any | SupportsInt], Sequence or 1-dim ArrayLike "
            f"but was of {type(input_data)}.",
        ),
        "invalid_input_upper": (
            ValueError,
            "has an inclusive upper bound of 1.0, but was",
        ),
        "invalid_input_lower": (
            ValueError,
            "has an inclusive lower bound of 0.0, but was",
        ),
    }

    error_type, error_msg = error_msgs[expected_error_type]
    with pytest.raises(error_type, match=re.escape(error_msg)):
        BitVector(input_data)


def test_representations() -> None:
    """Test str and repr."""
    bin_string = "111000"
    bit_vector = BitVector(bin_string)
    assert bin_string == str(bit_vector)
    assert bit_vector.__repr__() == "BitVector(111000)"


def test_len() -> None:
    """Test length of BitVector."""
    rng = np.random.default_rng()
    bit_array = rng.integers(low=0, high=2, size=20, dtype=np.uint8)
    for i in range(1, len(bit_array) + 1):
        assert i == len(BitVector(bit_array[:i]))


def test_binary_vector_equality() -> None:
    """Test (in)equality of BitVector objects."""
    input_string1 = "0101"
    input_string2 = "1010"
    input_list1 = [0, 1, 0, 1]
    input_list2 = [1, 0, 1, 0]

    # Equality for BitVector objects
    assert BitVector(input_string1) == BitVector(input_string1)
    assert BitVector(input_list1) == BitVector(input_list1)
    assert BitVector(input_string1) == BitVector(input_list1)

    # Not equality for BitVector objects
    assert BitVector(input_string1) != BitVector(input_string2)
    assert BitVector(input_list1) != BitVector(input_list2)
    assert BitVector(input_string1) != BitVector(input_list2)

    # Equality for non BitVector objects
    assert BitVector(input_string1) != input_string1
    assert BitVector(input_list1) != input_list1
    assert BitVector(input_string1) != input_list1
    assert BitVector(input_list1) != input_string1
    assert BitVector(input_list1) != "non-convertible-string"


def test_to_ising() -> None:
    """Test conversion of BitVector to Ising format."""
    input_list1 = np.array([0, 1, 0, 1], dtype=np.uint8)
    input_list2 = np.array([1, 0, 1, 0], dtype=np.uint8)
    expected_output1 = np.array([1, -1, 1, -1], dtype=np.int8)
    expected_output2 = np.array([-1, 1, -1, 1], dtype=np.int8)

    # Assuming BitVector is a class with a method to_ising
    bv1 = BitVector(input_list1)
    bv2 = BitVector(input_list2)

    # Test conversion to Ising format
    assert np.array_equal(bv1.to_ising(), expected_output1)
    assert np.array_equal(bv2.to_ising(), expected_output2)


def test_flip_indices() -> None:
    """Test flipping specific indices in a BitVector."""
    bv = BitVector("0101")

    # Flip index 0
    flipped_bv = bv.flip_indices(0)
    assert flipped_bv == BitVector("1101")

    # Flip indices 1 and 3
    flipped_bv = bv.flip_indices(1, 3)
    assert flipped_bv == BitVector("0000")

    # Flip indices 0, 2, and 3
    flipped_bv = bv.flip_indices(0, 2, 3)
    assert flipped_bv == BitVector("1110")

    # Test repeated indices
    flipped_bv = bv.flip_indices(1, 1)
    assert flipped_bv == bv.flip_indices(1)

    # Test invalid index
    expected_message = "index 4 is out of bounds for axis 0 with size 4"
    with pytest.raises(IndexError, match=expected_message):
        bv.flip_indices(4)

    # Flip index 0 and 3 inplace
    bv.flip_indices(0, 3, inplace=True)
    assert bv == BitVector("1100")


def test_iter_types() -> None:
    """Test iteration over BitVector."""
    bit_array = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.uint8)
    bit_vector = BitVector(bit_array)

    # Test the iteration
    for expected_value, bit_vector_value in zip(bit_array, bit_vector, strict=True):
        assert expected_value == bit_vector_value
        assert isinstance(bit_vector_value, np.uint8)  # Ensure the type is int

    # Ensure the iterator is exhausted correctly
    iterated_values = list(bit_vector)
    assert iterated_values == list(bit_array)


def test_slice() -> None:
    """Test iteration over slice."""
    bit_array = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.uint8)
    bit_vector = BitVector(bit_array)
    bit_vector_slice = bit_vector[2:]
    assert BitVector(bit_array[2:]) == bit_vector_slice


def test_array() -> None:
    """Test cast to array."""
    bit_array = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.uint8)
    bit_vector = BitVector(bit_array)
    assert np.array_equal(np.asarray(bit_vector), bit_array)


@pytest.mark.parametrize(
    ("input_1", "input_2"),
    [
        (BitVector([0, 0, 0]), BitVector([0, 0, 0])),
        (BitVector([0, 1, 0]), BitVector([0, 1, 0])),
        (BitVector([0, 0, 1]), BitVector((0, 0, 1))),
        (BitVector([1, 1, 1]), BitVector("111")),
        (BitVector("101010"), BitVector({0: 1, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0})),
    ],
)
def test_equal_hash(input_1: BitVector, input_2: BitVector) -> None:
    """Test hash dunder method"""
    assert hash(input_1) == hash(input_2)


@pytest.mark.parametrize(
    ("input_1", "input_2"),
    [
        (BitVector([0, 0, 0]), BitVector([1, 0, 0])),
        (BitVector([0, 0]), BitVector([0, 1, 0])),
        (BitVector([0, 0, 1, 1, 1, 1, 1]), BitVector((0, 0, 1))),
        (BitVector([1, 1]), BitVector("111")),
        (BitVector("10100"), BitVector({0: 1, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0})),
    ],
)
def test_unequal_hash(input_1: BitVector, input_2: BitVector) -> None:
    """Test hash dunder method"""
    assert hash(input_1) != hash(input_2)


@pytest.mark.parametrize(
    "binary_input",
    [
        "1010",
        (1, 1, 0, 0, 1, 1),
        (0, 0, 0, 1, 1, 1),
        "11",
        (1, 0, 1, 0, 1, 0),
        (1, 1, 1, 0, 0, 0),
        (0, 1, 0),
        (1, 1, 0, 0),
        (1, 1, 1, 1, 1, 1),
        (1, 0, 1),
        "1",
        (0, 1, 0, 1, 0, 1),
        (0, 0, 0),
        (1, 1, 1, 1, 1, 1, 1, 1),
    ],
)
def test_unequal_with_non_bitvector(binary_input: Any) -> None:
    """Test that hash BitVector is not equal to hash of input to BV."""
    bv = BitVector(binary_input)
    assert hash(bv) != hash(binary_input)


@pytest.mark.parametrize(
    "bit_vector",
    [
        [1, 1, 1, 1],
        np.array([1, 0, 1, 0]),
        (1, 0, 0, 0),
        "111111",
        {1: 0, 2: 1, 3: 1, 4: 1},
    ],
)
def test_json_serializable(bit_vector: BitVectorLike) -> None:
    """Tests if a BitVector can be jsonified"""
    bit_vector = BitVector(bit_vector)
    json_data = bit_vector.to_json()
    loaded_bit_vector: BitVector = BitVector.from_json(json_data)

    assert isinstance(loaded_bit_vector, BitVector)
    assert loaded_bit_vector == bit_vector


@pytest.mark.parametrize(
    "bit_vector",
    [
        [1, 1, 1, 1],
        np.array([1, 0, 1, 0]),
        (1, 0, 0, 0),
    ],
)
def test_bitvector_serializable(bit_vector: BitVectorLike) -> None:
    """Test save and load GBS."""
    bit_vector = BitVector(bit_vector)
    check_serializable(bit_vector)


@pytest.mark.parametrize(
    ("input_bit_vectors", "concatenated_bit_vector"),
    [
        ([[1, 0, 1]], [1, 0, 1]),
        ([[1, 0], [0, 1]], [1, 0, 0, 1]),
        ([[1, 1], [], [0, 0]], [1, 1, 0, 0]),
        ([], []),
        (
            [
                np.array([1 if i % 2 == 0 else 0 for i in range(1000)]),
                np.array([1 if i % 2 == 0 else 0 for i in range(1000, 2000)]),
            ],
            np.array([1 if i % 2 == 0 else 0 for i in range(2000)]),
        ),
    ],
)
def test_concatenate_bit_vectors(
    input_bit_vectors: list[BitVectorLike], concatenated_bit_vector: BitVectorLike
) -> None:
    result = BitVector.concatenate_bit_vectors(input_bit_vectors)
    assert result == BitVector(concatenated_bit_vector)


@pytest.mark.parametrize(
    ("first_bit_array", "second_bit_vector_like", "expected_concatenated_bit_array"),
    [
        ("11", [1, 1], [1, 1, 1, 1]),
        ([0], BitVector([1]), [0, 1]),
        ([1, 0], [], [1, 0]),
        (BitVector([]), "110", [1, 1, 0]),
        ([], [], []),
    ],
)
def test_concatenate(
    first_bit_array: BitVectorLike,
    second_bit_vector_like: BitVectorLike,
    expected_concatenated_bit_array: BitVectorLike,
) -> None:
    bv_1 = BitVector(first_bit_array)
    result = bv_1.concatenate(second_bit_vector_like)
    assert result == BitVector(expected_concatenated_bit_array)
