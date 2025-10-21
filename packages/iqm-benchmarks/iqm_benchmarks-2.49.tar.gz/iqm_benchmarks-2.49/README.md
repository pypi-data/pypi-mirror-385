# IQM Benchmarks

IQM Benchmarks is a suite of Quantum Characterization, Verification, and Validation (QCVV) tools for quantum computing. It is designed to be a comprehensive tool for benchmarking quantum hardware. The suite is designed to be modular, allowing users to easily add new benchmarks and customize existing ones. The suite is designed to be easy to use, with a simple API that allows users to run benchmarks with a single command.


Below is a list of the benchmarks currently available in the suite:
* Gates / Layers:
  - Standard Clifford Randomized Benchmarking [[Phys. Rev. A 85, 042311](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.85.042311) (2012)]
  - Interleaved Randomized Benchmarking [[Phys. Rev. Lett. 109, 080505](https://doi.org/10.1103/PhysRevLett.109.080505) (2012)]
  - Compressive Gate Set Tomography [[PRX Quantum 4, 010325](https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.4.010325) (2023)] (Optional dependencies required)
  - Mirror Randomized Benchmarking [[Phys. Rev. Lett. 129, 150502](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.129.150502) (2022)]
  - Error Per Layered Gate [[arXiv:2311.05933 [quant-ph]](https://arxiv.org/abs/2311.05933) (2023)]
* Holistic:
  - Quantum Volume [[Phys. Rev. A 100, 032328](https://doi.org/10.1103/PhysRevA.100.032328) (2019)]
  - CLOPS [[arXiv:2110.14108 [quant-ph]](https://arxiv.org/abs/2110.14108) (2021)]
* Entanglement:
  - GHZ State Fidelity [[arXiv:0712.0921 [quant-ph]](https://arxiv.org/abs/0712.0921) (2007)]
  - Graph State Bipartite Entanglement [[Adv. Quantum Technol., 2100061](https://doi.org/10.1002/qute.202100061) (2021)]
* Optimization:
  - Q-Score [[IEEE Trans. Quantum Eng., 2](https://doi.org/10.1109/TQE.2021.3090207) (2021)]

The project is split into different benchmarks, all sharing the `Benchmark` class or the legacy `BenchmarkBase` class. Each individual benchmark takes as an argument their own `BenchmarkConfigurationBase` class. All the (legacy) benchmarks executed at once are wrapped by the `BenchmarkExperiment` class, which handles dependencies among the benchmarks, storing the results, producing the plots...


## Installation _(latest release)_

[uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management.
With uv installed in your system, start a terminal in your machine and create a new Python environment

```sh
uv venv --python=3.11
```

> Note: refer to uv's documentation if there are problems setting up a Python environment.

After the command has run, read the output and make sure to use the prompt to activate the environment.
Then, you can install the latest release of the IQM Benchmarks by running:

```sh
uv pip install iqm-benchmarks
```

Supplied within the Python package there is an additional `requirements.txt` file containing locked, security scanned
dependencies. The file can be used to constrain installed dependencies either directly from the repo or by
extracting it from the PyPI package.

```sh
uv pip install --constraint requirements.txt iqm-benchmarks
```

## Optional dependencies

Optional dependencies like compressive gate set tomography and jupyter notebooks can be installed as follows:
```sh
uv pip install "iqm-benchmarks[mgst,examples]"
```
Current optional dependencies are:
* `examples`: Jupyter notebooks
* `mgst`: Compressive gate set tomography
* `test`: Code testing and Linting
* `docs`: Documentation building
* `cicd`: CICD tools

## Development installation _(latest changes)_

To install in development mode with all required dependencies, you can instead clone the
[repository](https://www.github.com/iqm-finland/iqm-benchmarks) and from the project directory run

```sh
uv pip install --constraint requirements.txt iqm-benchmarks --editable ."[test, docs, mgst]"
```

To run the tests, you can use the following command:

```sh
./test
```

To build the API documentation as HTML:

```sh
./docbuild
```

Update the requirements. This is necessary when you add a new dependency or update an existing one in `pyproject.toml`.
After this, any changes in the lockfile `requirements.txt` have to be committed.
The script upgrades locked dependencies defined in `pyproject.toml` within the given version ranges. However, transitive
dependencies are deliberately not upgraded automatically.

```sh
python update-requirements.py
```

## Characterize Physical Hardware

The IQM Benchmarks suite is designed to be used with real quantum hardware. To use the suite, you will need to have access to a quantum computer. The suite is designed to work with both IQM Resonance (IQM's quantum cloud service) and on-prem devices, but can be easily adapted to work with other quantum computing platforms.

To use the suite with IQM Resonance, you will need to set up an account and obtain an API token. You can then set the `IQM_TOKEN` environment variable to your API token. The suite will automatically use this token to authenticate with IQM Resonance.

```python
import os
os.environ["IQM_TOKEN"] = "your_token"
```

### Using a Jupyter notebook or Python script

You can easily set up one or more benchmarks by defining a configuration for them. For example, for Randomized, Interleaved and Mirror Benchmarking, or Quantum Volume:

```python
from iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb import InterleavedRBConfiguration
from iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb import MirrorRBConfiguration
from iqm.benchmarks.quantum_volume.quantum_volume import QuantumVolumeConfiguration

EXAMPLE_IRB = InterleavedRBConfiguration(
    qubits_array=[[3,4],[8,9]],
    sequence_lengths=[2**(m+1)-1 for m in range(7)],
    num_circuit_samples=30,
    shots=2**10,
    calset_id=None,
    parallel_execution=True,
    interleaved_gate = "iSwapGate",
    interleaved_gate_params = None,
    simultaneous_fit = ["amplitude", "offset"],
)

EXAMPLE_MRB = MirrorRBConfiguration(
    qubits_array=[[0,1],
                  [0,1,3,4],
                  [0,1,3,4,8,9],
                  [0,1,3,4,8,9,13,14],
                  [0,1,3,4,8,9,13,14,17,18]],
    depths_array=[[2**m for m in range(9)],
                  [2**m for m in range(8)],
                  [2**m for m in range(7)],
                  [2**m for m in range(6)],
                  [2**m for m in range(5)]],
    num_circuit_samples=10,
    num_pauli_samples=5,
    shots=2**8,
    two_qubit_gate_ensemble={"CZGate": 0.7, "iSwapGate": 0.3}, # {GATE: PROBABILITY}
    density_2q_gates=0.25,
    calset_id=None,
)

EXAMPLE_QV = QuantumVolumeConfiguration(
    num_circuits=800,
    shots=2**8,
    calset_id=None,
    num_sigmas=2,
    choose_qubits_routine="custom",
    custom_qubits_array=[[0,1,2,3], [0,1,3,4]],
    qiskit_optim_level=3,
    optimize_sqg=True,
    routing_method="sabre",
    physical_layout="fixed",
    max_circuits_per_batch=500,
    max_gates_per_batch=60_000, # Will be used if it renders a smaller max batch size than max_circuits_per_batch
    rem=True,
    mit_shots=1_000,
)
```

In order to execute them, you must specify a backend.
* for IQM Resonance this can be given as a simple string, such as "garnet" (together with your IQM Token environment variable)
* and for an on-prem device and IQM Resonance this can be defined using the URL of the quantum computer.

Also, you need to reference the benchmark configuration you want to run:

```python
from iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb import *
# import os
# os.environ["IQM_TOKEN"] = "your_token"

backend = IQMProvider("https://example-station.qc.iqm.fi/cocos/").get_backend()

EXAMPLE_EXPERIMENT = MirrorRandomizedBenchmarking(backend, EXAMPLE_MRB)
EXAMPLE_EXPERIMENT.run()
```

Full examples on how to run benchmarks and analyze the results can be found in the `examples` folder.

### Scheduled benchmarks using a CI/CD Pipeline

This repository can be setup to perform a scheduled (weekly, daily...) benchmark from a Gitlab/Github pipeline, executed on a real device. An example configuration is given in the `scheduled_experiments` folder.
