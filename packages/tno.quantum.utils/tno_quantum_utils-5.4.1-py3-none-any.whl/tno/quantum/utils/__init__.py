"""This package contains utility classes and methods for other TNO Quantum packages.

.. autodata:: tno.quantum.utils.BitVectorLike

A :py:class:`~typing.Union` representing objects from which a :py:class:`BitVector` can
be constructed. Among others, this includes bitstrings (e.g. ``"101010"``) and sequences
of bits (e.g. ``(1, 0, 1)`` or ``[0, 1, 0]``).
"""

import importlib.util

from tno.quantum.utils._base_arguments import BaseArguments
from tno.quantum.utils._base_config import BaseConfig
from tno.quantum.utils._bit_vector import BitVector, BitVectorLike
from tno.quantum.utils._utils import (
    check_equal,
    convert_to_snake_case,
    get_installed_subclasses,
)

__all__ = [
    "BaseArguments",
    "BaseConfig",
    "BitVector",
    "BitVectorLike",
    "check_equal",
    "convert_to_snake_case",
    "get_installed_subclasses",
]

if importlib.util.find_spec("pennylane") is not None:
    from tno.quantum.utils._backend_config import BackendConfig
    from tno.quantum.utils._noise_config import NoiseConfig

    __all__ += ["BackendConfig", "NoiseConfig"]

if importlib.util.find_spec("torch") is not None:
    from tno.quantum.utils._optimizer_config import OptimizerConfig

    __all__ += ["OptimizerConfig"]

__version__ = "5.4.1"
