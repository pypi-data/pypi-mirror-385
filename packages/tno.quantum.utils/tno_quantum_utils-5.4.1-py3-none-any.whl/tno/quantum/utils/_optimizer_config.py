"""This module contains the ``OptimizerConfig`` class."""

# ruff: noqa: PLC0415

from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from tno.quantum.utils._base_config import BaseConfig

if importlib.util.find_spec("torch") is not None:
    from torch.optim.optimizer import Optimizer

    @dataclass(init=False)
    class OptimizerConfig(BaseConfig[Optimizer]):
        """Configuration class for creating instances of a PyTorch optimizer.

        Currently only a selection of PyTorch optimizers are supported. See the
        documentation of :py:meth:`~OptimizerConfig.supported_items` for information on
        which optimizers are supported.

        Example:
            >>> import torch
            >>> from tno.quantum.utils import OptimizerConfig
            >>>
            >>> # List all supported optimizers
            >>> list(OptimizerConfig.supported_items())
            ['adagrad', 'adam', 'rprop', 'stochastic_gradient_descent']
            >>>
            >>> # Instantiate an optimizer
            >>> config = OptimizerConfig(name="adagrad", options={"lr": 0.5})
            >>> type(config.get_instance(params=[torch.rand(1)]))
            <class 'torch.optim.adagrad.Adagrad'>
        """

        def __init__(self, name: str, options: Mapping[str, Any] | None = None) -> None:
            """Init :py:class:`OptimizerConfig`.

            Args:
                name: Name of the :py:class:`torch.optim.optimizer.Optimizer` class.
                options: Keyword arguments to be passed to the optimizer. Must be a
                    mapping-like object keys being string objects. Values can be
                    anything depending on specific optimizer.

            Raises:
                TypeError: If `name` is not a string or `options` is not a mapping.
                KeyError: If `options` has a key that is not a string.
                KeyError: If `name` does not match any of the supported optimizers.
            """
            super().__init__(name=name, options=options)

        @staticmethod
        def supported_items() -> dict[str, type[Optimizer]]:
            """Obtain supported PyTorch optimizers.

            If PyTorch is installed then the following optimizers are supported:

                - Adagrad
                    - name: ``"adagrad"``
                    - options: see `Adagrad kwargs`__

                - Adam
                    - name: ``"adam"``
                    - options: see `Adam kwargs`__

                - Rprop
                    - name: ``"rprop"``
                    - options: see `Rprop kwargs`__

                - SDG:
                    - name: ``"stochastic_gradient_descent"``
                    - options: see `SDG kwargs`__


            __ https://pytorch.org/docs/stable/generated/torch.optim.Adagrad.html
            __ https://pytorch.org/docs/stable/generated/torch.optim.Adam.html
            __ https://pytorch.org/docs/stable/generated/torch.optim.Rprop.html
            __ https://pytorch.org/docs/stable/generated/torch.optim.SGD.html

            Raises:
                ModuleNotFoundError: If PyTorch can not be detected and no optimizers
                    can be found.

            Returns:
                Dictionary with supported optimizers by their name.
            """
            try:
                from torch.optim.adagrad import Adagrad
                from torch.optim.adam import Adam
                from torch.optim.rprop import Rprop
                from torch.optim.sgd import SGD

            except ModuleNotFoundError as exception:
                msg = "Torch can't be detected and hence no optimizers can be found."
                raise ModuleNotFoundError(msg) from exception

            else:
                return {
                    "adagrad": Adagrad,
                    "adam": Adam,
                    "rprop": Rprop,
                    "stochastic_gradient_descent": SGD,
                }
