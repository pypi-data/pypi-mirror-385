"""This module contains the ``NoiseConfig`` class."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable, Mapping
from typing import Any

from tno.quantum.utils._base_config import BaseConfig
from tno.quantum.utils.noise import depolarizing
from tno.quantum.utils.serialization import Serializable
from tno.quantum.utils.validation import check_instance

if importlib.util.find_spec("pennylane") is not None:
    import pennylane as qml
    from pennylane.devices import Device

    if int(qml.__version__.split(".")[1]) >= 39:
        from pennylane.transforms import decompose
    else:
        from pennylane.devices.preprocess import decompose

    def device_prepend_decompose(device: Device, gate_set: list[str]) -> Device:
        """Create a transformed device with prepended decompose preprocessing."""

        class TransformedDevice(type(device)):  # type: ignore[misc]
            """A transformed device with updated decompose method."""

            def __init__(
                self,
                original_device: Device,
                transform: qml.transforms.core.TransformDispatcher,
                gate_set: list[str],
            ) -> None:
                for key, value in original_device.__dict__.items():
                    self.__setattr__(key, value)
                self._transform = transform
                self._original_device = original_device
                self._gate_set = gate_set

            def __repr__(self) -> str:
                return (
                    f"Transformed Device({self._original_device.__repr__()}"
                    f" with additional initial preprocess transform"
                    f" {self._transform})"
                )

            def _stopping_condition(self, op: qml.operation.Operator) -> bool:
                return op.name in self._gate_set

            def preprocess(
                self,
                execution_config: qml.devices.ExecutionConfig
                | None = qml.devices.DefaultExecutionConfig,
            ) -> tuple[
                qml.transforms.core.TransformProgram,
                qml.devices.ExecutionConfig,
            ]:
                program, config = self._original_device.preprocess(execution_config)

                if int(qml.__version__.split(".")[1]) >= 39:
                    program.insert_front_transform(
                        self._transform, gate_set=self._stopping_condition
                    )
                else:
                    program.insert_front_transform(
                        self._transform,
                        stopping_condition=self._stopping_condition,
                    )
                return program, config

        return TransformedDevice(device, decompose, gate_set)

    class NoiseConfig(BaseConfig[Device]):
        """Configuration class for creating noise models for PennyLane devices.

        The :py:meth:`get_instance` method of :py:class:`NoiseConfig` class can be
        used to transform a device into a noisy device.

        Example:
            >>> import pennylane as qml
            >>> from tno.quantum.utils import NoiseConfig
            >>>
            >>> # List all supported noise models
            >>> list(NoiseConfig.supported_items())
            ['depolarizing']
            >>>
            >>> # Create a noisy device from a device
            >>> device = qml.device("default.mixed", wires=1)
            >>> config = NoiseConfig(name="depolarizing", options={
            ...     "p": 0.01,
            ... })
            >>> noisy_device = config.get_instance(device)
            >>>
            >>> # Or create a noise configuration from a `qml.NoiseModel`
            >>> model = qml.NoiseModel(...)  # doctest: +SKIP
            >>> config = NoiseConfig.from_model(model)  # doctest: +SKIP
            >>> noisy_device = config.get_instance(device)  # doctest: +SKIP
        """

        def __init__(
            self,
            name: str,
            options: Mapping[str, Any] | None = None,
            *,
            custom: Callable[[Device], Device] | None = None,
        ) -> None:
            """Init :py:class:`NoiseConfig`.

            Args:
                name: Name used to determine the name of the to instantiate class.
                options: Keyword arguments to be passed to the constructor of the class.
                custom: Custom device transform function.
            """
            if custom is None:
                super().__init__(name, options)
            else:
                self._name = ""
                self._options = {}
            self._custom = custom

        @staticmethod
        def from_model(
            model: qml.NoiseModel, gates: list[str] | None = None
        ) -> NoiseConfig:
            """Create noise configuration from custom model.

            Args:
                model: PennyLane noise model.
                gates: List of gates into which the circuit is decomposed before
                    executed on the device. See the `list of operations <https://docs.pennylane.ai/en/stable/introduction/operations.html>`_.
            """
            # Validate arguments
            model = check_instance(model, "model", qml.NoiseModel)
            if gates is not None and (
                not isinstance(gates, list)
                or any(not isinstance(gate, str) for gate in gates)
            ):
                msg = "Argument `gates` must be a list of strings"
                raise ValueError(msg)

            # Define transform function based on model and gates
            def transform(device: Device) -> Device:
                if gates is not None:
                    device = device_prepend_decompose(device, gates)
                return qml.add_noise(device, model)

            return NoiseConfig("", custom=transform)

        def get_instance(self, device: Device, *args: Any, **kwargs: Any) -> Device:
            if self._custom is not None:
                return self._custom(device, *args, **kwargs)
            return super().get_instance(device, *args, **kwargs)

        @staticmethod
        def supported_items() -> dict[str, Callable[..., Device]]:
            return {"depolarizing": depolarizing}

        def _serialize(self) -> dict[str, Any]:
            if self._custom is not None:
                msg = (
                    "Serialization of noise configurations with custom transform "
                    "method is not supported yet."
                )
                raise NotImplementedError(msg)

            return {"name": self.name, "options": Serializable.serialize(self.options)}
