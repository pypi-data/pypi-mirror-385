"""This module contains tests for ``tno.quantum.utils._base_config``."""

from __future__ import annotations

import pickle
import sys
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pennylane as qml
import pytest
import torch
from numpy.typing import ArrayLike, NDArray
from pennylane.devices import DefaultQubit
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import euclidean_distances
from sklearn.utils.estimator_checks import estimator_checks_generator
from sklearn.utils.multiclass import unique_labels
from sklearn.utils.validation import check_is_fitted, validate_data
from torch.optim.adagrad import Adagrad
from torch.optim.adam import Adam
from torch.optim.rprop import Rprop
from torch.optim.sgd import SGD

from tno.quantum.utils import BackendConfig, BaseConfig, NoiseConfig, OptimizerConfig
from tno.quantum.utils.serialization import check_serializable
from tno.quantum.utils.test.test_base_arguments import GroundLevelArguments

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray
    from torch.optim.optimizer import Optimizer
    from torchtyping import TensorType


# ruff: noqa: N803, N806


# region BaseConfig
class ValidConfig(BaseConfig[int | GroundLevelArguments]):
    """Config used for testing a valid configuration"""

    @staticmethod
    def supported_items() -> dict[str, Any]:
        return {
            "int": int,
            "ground_level_arguments": GroundLevelArguments,
        }


def test_valid_configuration_int() -> None:
    """Test valid configuration type int."""
    config = ValidConfig(name="int")
    assert config.name == "int"
    assert config.options == {}
    assert config.supported_items() == {
        "int": int,
        "ground_level_arguments": GroundLevelArguments,
    }

    # Test additional constructor arguments
    additional_arg = 5
    assert config.get_constructor() is int
    assert config.get_instance(additional_arg) == additional_arg


def test_valid_configuration_ground_level_arguments() -> None:
    """Test valid configuration type ground level arguments."""
    config = ValidConfig(
        name="ground_level_arguments", options={"name": "test", "size": 5}
    )
    assert config.name == "ground_level_arguments"
    assert config.options == {"name": "test", "size": 5}
    assert config.supported_items() == {
        "int": int,
        "ground_level_arguments": GroundLevelArguments,
    }
    assert config.get_constructor() is GroundLevelArguments
    assert config.get_instance() == GroundLevelArguments(name="test", size=5)

    # Test additional keyword constructor arguments
    assert config.get_instance(size=6) == GroundLevelArguments(name="test", size=6)


def test_invalid_configuration_name() -> None:
    """Test invalid configuration name."""
    error_msg = "does not match any of the supported items"
    with pytest.raises(KeyError, match=error_msg):
        ValidConfig(name="unsupported_class")


# region BackendConfig


def test_default_qubit() -> None:
    """Test get default qubit PennyLane device."""

    number_of_shots = 123
    number_of_wires = 11
    backend_config = BackendConfig(
        name="default.qubit",
        options={"seed": 42, "shots": number_of_shots, "wires": number_of_wires},
    )
    assert callable(backend_config.get_constructor())
    device = backend_config.get_instance()
    assert isinstance(device, DefaultQubit)
    assert device.shots.total_shots == number_of_shots
    assert device.wires.tolist() == list(range(number_of_wires))
    assert str(device._rng).startswith("Generator(PCG64)")


# region NoiseConfig


@pytest.fixture(name="noise_config")
def noise_config() -> NoiseConfig:
    """Simple noise model that adds an RX(0.5) gate to every RZ gate."""
    condition = qml.noise.op_eq(qml.RZ)
    noise = qml.noise.partial_wires(qml.RX, 0.5)
    model = qml.NoiseModel({condition: noise})
    return NoiseConfig.from_model(model)


@pytest.fixture(name="noise_config_with_gates")
def noise_config_with_gates() -> NoiseConfig:
    """Simple noise model that adds an RX(0.5) gate to every RZ gate."""
    condition = qml.noise.op_eq(qml.RZ)
    noise = qml.noise.partial_wires(qml.RX, 0.5)
    model = qml.NoiseModel({condition: noise})
    return NoiseConfig.from_model(model, ["RZ"])


def test_noise_is_applied(noise_config: NoiseConfig) -> None:
    """Test noise model passed via BackendConfig is correctly applied to circuit."""
    noisy_device = BackendConfig(
        name="default.mixed", options={"wires": 1}, noise=noise_config
    ).get_instance()

    @qml.qnode(noisy_device)  # type: ignore[misc]
    def circuit(phi: float) -> qml.measurements.StateMP:
        qml.RZ(phi, wires=0)
        qml.RZ(-phi, wires=0)
        return qml.state()

    expected = np.array([[1.0, 0.0], [0.0, 0.0]])
    fidelity = qml.math.fidelity(circuit(0.0), expected)
    threshold = 0.9

    assert fidelity < threshold


def test_noise_is_not_applied(noise_config: NoiseConfig) -> None:
    """Test noise model passed via BackendConfig is not applied to circuit if the
    circuit is not sufficiently decomposed."""
    noisy_device = BackendConfig(
        name="default.mixed", options={"wires": 1}, noise=noise_config
    ).get_instance()

    hamiltonian = qml.Hamiltonian([0.5], [qml.Z(0)])

    @qml.qnode(noisy_device)  # type: ignore[misc]
    def circuit(phi: float) -> qml.measurements.StateMP:
        qml.ApproxTimeEvolution(hamiltonian, phi, 1)
        qml.ApproxTimeEvolution(hamiltonian, -phi, 1)
        return qml.state()

    expected = np.array([[1.0, 0.0], [0.0, 0.0]])
    fidelity = qml.math.fidelity(circuit(0.0), expected)

    assert fidelity == pytest.approx(1.0)


def test_noise_is_applied_when_decomposed(noise_config_with_gates: NoiseConfig) -> None:
    """Test noise model passed via BackendConfig is correctly applied to circuit when
    the circuit is sufficiently decomposed."""
    noisy_device = BackendConfig(
        name="default.mixed",
        options={"wires": 1},
        noise=noise_config_with_gates,
    ).get_instance()

    hamiltonian = qml.Hamiltonian([0.5], [qml.Z(0)])

    @qml.qnode(noisy_device)  # type: ignore[misc]
    def circuit(phi: float) -> qml.measurements.StateMP:
        qml.ApproxTimeEvolution(hamiltonian, phi, 1)
        qml.ApproxTimeEvolution(hamiltonian, -phi, 1)
        return qml.state()

    expected = np.array([[1.0, 0.0], [0.0, 0.0]])
    fidelity = qml.math.fidelity(circuit(0.0), expected)
    threshold = 0.9

    assert fidelity < threshold


@pytest.mark.parametrize(
    ("p", "check"),
    [
        (0.5, lambda fidelity: fidelity < 0.9),  # noqa: PLR2004
        ({"RX": 0.5}, lambda fidelity: fidelity == pytest.approx(1.0)),
        ({"Hadamard": 0.5}, lambda fidelity: fidelity < 0.9),  # noqa: PLR2004
    ],
)
def test_depolarizing_one_qubit(
    p: float | dict[str, float], check: Callable[[float], bool]
) -> None:
    """Test the depolarizing noise model on one qubit."""
    noisy_device = BackendConfig(
        name="default.mixed",
        options={"wires": 1},
        noise={"name": "depolarizing", "options": {"p": p}},
    ).get_instance()

    @qml.qnode(noisy_device)  # type: ignore[misc]
    def circuit() -> qml.measurements.StateMP:
        qml.Hadamard(0)
        qml.Hadamard(0)
        return qml.state()

    expected = np.array([[1.0, 0.0], [0.0, 0.0]])
    fidelity = qml.math.fidelity(circuit(), expected)

    assert check(fidelity)


def test_depolarizing_two_qubits() -> None:
    """Test the depolarizing noise model on two qubits."""
    noisy_device = BackendConfig(
        name="default.mixed",
        options={"wires": 2},
        noise={"name": "depolarizing", "options": {"p": 0.5}},
    ).get_instance()

    @qml.qnode(noisy_device)  # type: ignore[misc]
    def circuit() -> qml.measurements.StateMP:
        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[0, 1])
        return qml.state()

    expected = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ]
    )
    fidelity = qml.math.fidelity(circuit(), expected)
    threshold = 0.9

    assert fidelity < threshold


# region OptimizerConfig


@pytest.fixture(name="parameters")
def parameters_fixture() -> Iterable[TensorType]:
    """Iterable PyTorch tensor fixture."""
    return [torch.rand(1)]


@pytest.mark.parametrize(
    ("optimizer_name", "expected_optimizer"),
    [
        ("adagrad", Adagrad),
        ("adam", Adam),
        ("rprop", Rprop),
        ("stochastic_gradient_descent", SGD),
    ],
)
def test_get_optimizer_by_config(
    parameters: Iterable[TensorType],
    optimizer_name: str,
    expected_optimizer: type[Optimizer],
) -> None:
    """Test get optimizer by correct optimizer name."""
    optimizer_config = OptimizerConfig(name=optimizer_name, options={})
    parameters = [torch.rand(1)]
    opt = optimizer_config.get_instance(params=parameters)
    assert isinstance(opt, expected_optimizer)


@pytest.mark.parametrize(
    ("optimizer_name", "learning_rate"),
    [
        ("adagrad", 0.02),
        ("adam", 0.05),
        ("rprop", 0.10),
        ("stochastic_gradient_descent", 2),
    ],
)
def test_set_learning_rate_for_optimizer(
    parameters: Iterable[TensorType], optimizer_name: str, learning_rate: float
) -> None:
    """Test setting learning rate to optimizer via options."""
    options = {"lr": learning_rate}
    optimizer_config = OptimizerConfig(name=optimizer_name, options=options)

    opt = optimizer_config.get_instance(params=parameters)
    assert opt.param_groups[0]["lr"] == learning_rate


def test_empty_supported_optimizers_if_no_pytorch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test empty supported optimizers if PyTorch is not installed."""
    for module in sys.modules:
        if module.startswith("torch"):
            monkeypatch.setitem(sys.modules, module, None)
    expected_message = "Torch can't be detected and hence no optimizers can be found."
    with pytest.raises(ModuleNotFoundError, match=expected_message):
        assert OptimizerConfig.supported_items()


# region Sklearn estimator compatibility


class SklearnClassifier(ClassifierMixin, BaseEstimator):  # type:ignore[misc]
    """Simple classifier to check Config objects can be used as argument."""

    def __init__(self, config: BackendConfig | Mapping[str, Any] | None = None) -> None:
        self.config = config

    def fit(self, X: ArrayLike, y: ArrayLike) -> SklearnClassifier:
        """Simple fit example implementation."""

        # Validate possible usage of BackendConfig config
        if self.config is None:
            config = BackendConfig(name="default.qubit")
        else:
            config = BackendConfig.from_mapping(self.config)
        config.get_instance()

        # Simple dummy classifier
        X, y = validate_data(self, X, y)
        X, y = np.array(X), np.array(y)
        self.classes_ = unique_labels(y)
        self.n_features_in_ = X.shape[1]
        self.X_ = X
        self.y_ = y
        return self

    def predict(self, X: ArrayLike) -> NDArray[Any]:
        """Simple predict example implementation."""
        check_is_fitted(self)
        X = validate_data(self, X, reset=False)
        closest = np.argmin(euclidean_distances(X, self.X_), axis=1)
        predictions: NDArray[Any] = self.y_[closest]
        return predictions


@pytest.mark.parametrize(
    "config",
    [None, {"name": "default.qubit"}, BackendConfig(name="default.qubit")],
)
def test_sklearn_compliance(
    tmp_path: Path, config: None | Mapping[str, Any] | BackendConfig
) -> None:
    """Test if simple classifier is sklearn compatible."""

    classifier = SklearnClassifier(config)
    for estimator, check in estimator_checks_generator(classifier):
        check(estimator)

    # Test classifier remains picklable:
    with Path(tmp_path / "model.pkl").open("wb") as file:
        pickle.dump(classifier, file)

    with Path(tmp_path / "model.pkl").open("rb") as file:
        loaded_model: SklearnClassifier = pickle.load(file)  # noqa: S301

    assert loaded_model.config == config


# region custom supported items


class CustomBackend:
    pass


def test_register_custom_item() -> None:
    """Test adding custom items to a config"""
    # Register custom backend
    BackendConfig.register_custom_item(name="custom_name", item=CustomBackend)
    supported_custom_items = BackendConfig.supported_custom_items()
    assert "custom_name" in supported_custom_items
    assert supported_custom_items["custom_name"] == CustomBackend

    # Create instance
    backend_config = BackendConfig(name="custom_name")
    assert isinstance(backend_config.get_instance(), CustomBackend)


def test_raise_error_invalid_name_already_in_supported_items() -> None:
    """Test raise error if item name is in supported items."""
    error_msg = "already exists a similar named item within `supported_items`"
    with pytest.raises(ValueError, match=error_msg):
        BackendConfig.register_custom_item(name="default.qubit", item=CustomBackend)


def test_raise_error_invalid_name_already_in_supported_custom_items() -> None:
    """Test raise error if item name is in supported custom items."""
    error_msg = "already exists a similar named item within `supported_custom_items`"
    BackendConfig.register_custom_item(
        name="custom_name_exist_test", item=CustomBackend
    )
    with pytest.raises(ValueError, match=error_msg):
        BackendConfig.register_custom_item(
            name="custom_name_exist_test", item=CustomBackend
        )


def test_raise_error_invalid_item() -> None:
    """Test raise error if item is not class or type object."""
    invalid_item = CustomBackend()
    error_msg = f"Provided item {invalid_item} is not a class or callable object."
    with pytest.raises(TypeError, match=error_msg):
        BackendConfig.register_custom_item(name="custom_name", item=invalid_item)  # type: ignore[arg-type]


# region Serializable


def test_config_serializable() -> None:
    """Test load JSON config from file."""
    check_serializable(
        BackendConfig(
            name="default.qubit", options={"seed": 42, "shots": 123, "wires": 11}
        )
    )
