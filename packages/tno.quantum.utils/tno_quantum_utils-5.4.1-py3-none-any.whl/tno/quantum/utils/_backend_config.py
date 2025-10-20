"""This module contains the ``BackendConfig`` class."""

from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import partial
from typing import Any

from tno.quantum.utils._base_config import BaseConfig
from tno.quantum.utils._noise_config import NoiseConfig

if importlib.util.find_spec("pennylane") is not None:
    import pennylane as qml
    from pennylane.devices import Device

    @dataclass(init=False)
    class BackendConfig(BaseConfig[Device]):
        """Configuration class for creating PennyLane device instances.

        Supported backends can be found by calling
        :py:meth:`~BackendConfig.supported_items`.

        Example:
            >>> from tno.quantum.utils import BackendConfig
            >>>
            >>> # List all supported backends
            >>> sorted(BackendConfig.supported_items())[:4]
            ['default.clifford', 'default.gaussian', 'default.mixed', 'default.qubit']
            >>>
            >>> # Instantiate a backend
            >>> config = BackendConfig(name="default.qubit", options={"wires": 5})
            >>> type(config.get_instance())
            <class 'pennylane.devices.default_qubit.DefaultQubit'>
        """

        def __init__(
            self,
            name: str,
            options: Mapping[str, Any] | None = None,
            *,
            noise: NoiseConfig | dict[str, Any] | None = None,
        ) -> None:
            """Init :py:class:`BackendConfig`.

            Args:
                name: Name of the PennyLane :py:class:`~pennylane.devices.Device`,
                    for example ``"default.qubit"``.
                options: Keyword arguments to be passed to the constructor of the device
                    class.
                noise: Configuration for noise model to apply to the model.

            Raises:
                TypeError: If `name` is not a string or `options` is not a mapping.
                KeyError: If `options` has a key that is not a string.
                KeyError: If `name` does not match any of the supported backends.
            """
            super().__init__(name=name, options=options)
            self._noise = NoiseConfig.from_mapping(noise) if noise is not None else None

        @property
        def noise(self) -> NoiseConfig | None:
            """Configuration for noise model to apply to the model."""
            return self._noise

        @staticmethod
        def supported_items() -> dict[str, Callable[..., Device]]:
            """Obtain all supported PennyLane backend devices.

            Returns:
                Dictionary with callable that instantiate Pennylane Device instances.
            """
            return {
                device_name: partial(qml.device, name=device_name)
                for device_name in qml.plugin_devices
            }

        def get_instance(
            self, *additional_args: Any, **additional_kwargs: Any
        ) -> Device:
            # Instantiate device
            device = super().get_instance(*additional_args, **additional_kwargs)

            # Add noise (if applicable)
            if self._noise is not None:
                device = self._noise.get_instance(device)

            return device
