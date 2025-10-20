"""This module contains the ``BitVector`` class and ``BitVectorLike`` type alias."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from copy import deepcopy
from typing import TYPE_CHECKING, Any, SupportsInt, TypeAlias, overload

import numpy as np
from numpy.typing import ArrayLike

from tno.quantum.utils.serialization import Serializable
from tno.quantum.utils.validation import check_arraylike, check_binary

BitVectorLike: TypeAlias = (
    str | Mapping[Any, SupportsInt] | Sequence[SupportsInt] | ArrayLike
)

if TYPE_CHECKING:
    import sys
    from typing import Self

    from numpy.typing import DTypeLike, NDArray

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class BitVector(Sequence[np.uint8], Serializable):
    """Class representing a vector of bits.

    This class can be initialized from multiple datatypes, such as strings,
    dictionaries, lists, and NumPy arrays. The input data is converted and stored as
    a Numpy :py:class:`~numpy.ndarray`.

    Example:
        >>> from tno.quantum.utils import BitVector
        >>>
        >>> BitVector("1001")
        BitVector(1001)
        >>> BitVector([1, 0, 0, 1])
        BitVector(1001)
        >>> BitVector((1, 0, 0, 1))
        BitVector(1001)
    """

    def __init__(
        self,
        bits: BitVectorLike,
    ) -> None:
        """Init :py:class:`BitVector`.

        Args:
            bits: Bits used to construct a binary vector.

        Raises:
            TypeError: If `bits` is not of a supported type.
            ValueError: If `bits` contains items that can not be converted to int.
        """
        error_msg = (
            "The provided input `bits` must be a str, "
            "Mapping[Any | SupportsInt], Sequence or 1-dim ArrayLike "
            f"but was of {type(bits)}."
        )

        if not isinstance(bits, (str, Mapping, Sequence)):
            try:
                bits = check_arraylike(bits, "bits", ndim=1)
            except ValueError as exception:
                raise TypeError(error_msg) from exception

        elif isinstance(bits, Mapping):
            try:
                bits = [int(bit) for bit in bits.values()]
            except ValueError as exception:
                raise TypeError(error_msg) from exception

        self._bits = np.fromiter(
            (check_binary(bit, f"{bit}") for bit in bits),
            dtype=np.uint8,
            count=len(bits),
        )

    @property
    def bits(self) -> NDArray[np.uint8]:
        """Returns bits as :py:class:`~numpy.ndarray`."""
        return self._bits

    def __str__(self) -> str:
        """Returns string representation of binary vector."""
        return "".join(map(str, self.bits))

    def __len__(self) -> int:
        """Returns length of the binary vector."""
        return len(self.bits)

    def __iter__(self) -> Iterator[np.uint8]:
        """Returns iterator for the binary vector."""
        return iter(self.bits)

    @overload
    def __getitem__(self, index: int) -> np.uint8: ...

    @overload
    def __getitem__(self, index: slice) -> BitVector: ...

    def __getitem__(self, index: int | slice) -> np.uint8 | BitVector:
        """Get integer or slice object from BitVector object."""
        if isinstance(index, int):
            # Ensure the return type is np.uint8
            single_result: np.uint8 = self.bits[index]
            return single_result
        return BitVector(self.bits[index])

    def __repr__(self) -> str:
        """Returns detailed string representation of the binary vector."""
        return f"{self.__class__.__name__}({self.__str__()})"

    def __eq__(self, other: Any) -> bool:
        """Checks if two bitvector instances are equal."""
        if isinstance(other, BitVector):
            return np.array_equal(self.bits, other.bits)
        return False

    def __array__(self, dtype: DTypeLike = None, *, copy: bool = True) -> NDArray[Any]:
        """Returns the bitvector as an array."""
        return np.array(self.bits, dtype=dtype, copy=copy)

    def __hash__(self) -> int:
        """Provides unique hash for bitvector."""
        return hash((self.__class__.__name__, tuple(self.bits)))

    def to_ising(self) -> NDArray[np.int8]:
        """Returns the current bitvector as an array in Lenz-Ising format.

        In particular, every zero bit is mapped to 1 and every one bit is mapped to -1.
        """
        return 1 - 2 * self.bits.astype(np.int8)

    def flip_indices(self, *indices: int, inplace: bool = False) -> BitVector:
        """Flip the bits at the specified indices.

        Args:
            indices: Indices of the bits to flip. Each index must be an integer
                greater than or equal to 0 and less than the length of the bit vector.
                Repeated indices will be applied only once.
            inplace: If ``True``, modify current instance. If ``False``, return a new
                instance.

        Returns:
            A new :py:class:`BitVector` instance with the specified bits flipped.
        """
        indices_list = np.fromiter(indices, dtype=int)

        if inplace:
            self.bits[indices_list] = -self.bits[indices_list] + 1
            return self

        bits_copy = deepcopy(self.bits)
        bits_copy[indices_list] = -bits_copy[indices_list] + 1
        return BitVector(bits_copy)

    @classmethod
    def concatenate_bit_vectors(cls, bit_vectors: Iterable[BitVectorLike]) -> Self:
        """Concatenate multiple bitvectors into a single :py:class:`BitVector` instance.

        Args:
            bit_vectors: A list of objects that can be converted to
                :py:class:`BitVector`.

        Returns:
            A new instance of the class with the concatenated bit vectors. If no bit
            vectors are provided (i.e., the list is empty), an empty
            :py:class:`BitVector` is returned.
        """
        if not bit_vectors:
            return cls([])

        concatenated_bit_vectors = np.concatenate(
            [BitVector(bit_vector_like).bits for bit_vector_like in bit_vectors]
        )
        return cls(concatenated_bit_vectors)

    def concatenate(self, other: BitVectorLike) -> BitVector:
        """Concatenate a bitvector with a :py:const:`~tno.quantum.utils.BitVectorLike` to a bitvector.

        Args:
            other: The :py:const:`~tno.quantum.utils.BitVectorLike` instance to
                concatenate with.

        Returns:
            A new :py:class:`BitVector` instance with concatenated bits.
        """  # noqa: E501
        return BitVector.concatenate_bit_vectors(bit_vectors=[self, other])

    def _serialize(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {"bits": str(self)}
