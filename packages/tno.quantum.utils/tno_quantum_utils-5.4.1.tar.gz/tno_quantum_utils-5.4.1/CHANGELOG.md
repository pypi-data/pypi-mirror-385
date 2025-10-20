
# 5.4.1 (2025 - 10 - 19)

Support for `python3.9` is dropped.

### Features

* **Noise models:** Added support for noise to our `BackendConfig`. Introduced `NoiseConfig`.
* Serializable objects now have default `eq` and `hash`:
* Small additions such as `check_equal` and `get_constructor` for configs.

# 5.1.0 (2025 - 05 - 12)

### Features

* **BaseConfig & BaseConfiguration:** Base arguments and configuration data classes.
* **BackendConfig:** Configuration class to select Pennylane backend.
* **OptimizerConfig:** Configuration class to select pytorch optimizer.
* **BitVectorLike:** ``BitVector`` class and ``BitVectorLike`` type alias.
* **Validation:** Generic validation methods.
* **Serialization:** The module provides the tools to give any class support for default serialization and deserialization.

