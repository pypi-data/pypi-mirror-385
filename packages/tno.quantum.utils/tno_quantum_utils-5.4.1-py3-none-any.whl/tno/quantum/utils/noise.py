"""This module contains various standard noise models.

These standard noise models can be used by themselves or through the
:py:class:`~tno.quantum.utils.NoiseConfig` class.
"""

import importlib.util
from typing import Any

from tno.quantum.utils.validation import check_kwarglike, check_real

if importlib.util.find_spec("pennylane"):
    import pennylane as qml
    from pennylane.devices import Device

    def depolarizing(device: Device, **kwargs: Any) -> Device:
        """Depolarizing noise model.

        This noise model applies :py:class:`~pennylane.DepolarizingChannel` after
        certain gates. If the argument `p` is a :py:const:`float`, a depolarizing
        channel with probability `p` is applied to each wire after every gate.
        If the argument `p` is a :py:const:`dict[str, float]`, then a depolarizing
        channel is applied to each wire after every gate whose name is a key of `p`,
        with probability the corresponding value.

        Args:
            device: Device to transform.
            p: Probability of the :py:class:`~pennylane.DepolarizingChannel`.
                Default is `0.01`.
            kwargs: Not used.
        """
        p = kwargs.get("p", 0.01)
        if isinstance(p, float):
            p = check_real(p, "p", l_bound=0.0, u_bound=1.0)
        else:
            p = check_kwarglike(p, "p")

        condition = qml.noise.wires_in(device.wires)

        def noise(op: qml.operation.Operator, **kwargs: Any) -> None:
            q = p if isinstance(p, float) else p.get(op.name, None)
            if q is not None:
                for wire in op.wires:
                    qml.DepolarizingChannel(q, wire)

        model = qml.NoiseModel({condition: noise})
        return qml.add_noise(device, model)
