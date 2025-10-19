---
file_format: mystnb
kernelspec:
  name: python3
mystnb:
  number_source_lines: true
---

```{code-cell} ipython3
:tags: [remove-cell]
%config InlineBackend.figure_formats = ['svg']
```

# Parameter Space

The {func}`~mqt.bench.get_benchmark` function has the following signature:

- `benchmark` (see {doc}`details <benchmark_selection>`):

```{code-cell} ipython3
:tags: [hide-input]
from mqt.bench.benchmarks import get_available_benchmark_names

print(get_available_benchmark_names())
```

- `level`: BenchmarkLevel.ALG, BenchmarkLevel.INDEP, BenchmarkLevel.NATIVEGATES, BenchmarkLevel.MAPPED
- `circuit_size`: Define the number of qubits in the circuit.
- `target`: Target, which can also be instantiated based on gatesets using `get_target_for_gateset(gateset_name)` or based on a device using `get_device(device_name)`.
  Possible values for `gateset_name`:

```{code-cell} ipython3
:tags: [hide-input]
from mqt.bench.targets import get_available_gateset_names

print(get_available_gateset_names())
```

(required for "nativegates" level)

Possible values for `device_name`:

```{code-cell} ipython3
:tags: [hide-input]
from mqt.bench.targets import get_available_device_names

print(get_available_device_names())
```

(required for "mapped" level)

- `opt_level`: Optimization level for `"qiskit"` (`0`-`3`).
- `random_parameters`: Assign random parameters to the circuit's parameters if they exist.
- `generate_mirror_circuit`: Generate the mirror version (U @ U.inverse()) of the benchmark.

## Native Gate-Set Support

So far, MQT Bench supports the following native gatesets:

```{code-cell} ipython3
:tags: [hide-input]
from mqt.bench.targets import get_gateset, get_available_gateset_names

for num, gateset_name in enumerate(get_available_gateset_names()):
    print(f"{num+1}: {gateset_name} → {get_gateset(gateset_name)}")
```

## Device Support

So far, MQT Bench supports the following devices:

```{code-cell} ipython3
:tags: [hide-input]
from mqt.bench.targets import get_device, get_available_device_names

for num, device_name in enumerate(get_available_device_names()):
    print(f"{num+1}: {device_name} with {get_device(device_name).num_qubits} qubits")
```

Examples how to use the {func}`~.mqt.bench.get_benchmark` method for all four abstraction levels can be found on the {doc}`Quickstart jupyter notebook <quickstart>`.
