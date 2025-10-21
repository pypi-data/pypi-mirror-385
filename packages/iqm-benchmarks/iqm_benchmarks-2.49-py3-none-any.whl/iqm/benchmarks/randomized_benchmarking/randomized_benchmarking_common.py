# Copyright 2024 IQM Benchmarks developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Common functions for Randomized Benchmarking-based techniques
"""
from copy import deepcopy
from importlib import import_module
from itertools import chain
import os
import pickle
import random
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, cast

from lmfit import Parameters, minimize
from lmfit.minimizer import MinimizerResult
from matplotlib.collections import PolyCollection
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Clifford, random_clifford
import xarray as xr

from iqm.benchmarks.logging_config import qcvv_logger
from iqm.benchmarks.randomized_benchmarking.multi_lmfit import create_multi_dataset_params, multi_dataset_residual
from iqm.benchmarks.utils import get_iqm_backend, marginal_distribution, submit_execute, timeit
from iqm.iqm_client.models import CircuitCompilationOptions
from iqm.qiskit_iqm import IQMCircuit as QuantumCircuit
from iqm.qiskit_iqm import optimize_single_qubit_gates
from iqm.qiskit_iqm.iqm_backend import IQMBackendBase


# pylint: disable=too-many-lines


def compute_inverse_clifford(qc_inv: QuantumCircuit, clifford_dictionary: Dict) -> Optional[QuantumCircuit]:
    """Function to compute the inverse Clifford of a circuit
    Args:
        qc_inv (QuantumCircuit): The Clifford circuit to be inverted
        clifford_dictionary (Dict): A dictionary of Clifford gates labeled by (de)stabilizers
    Returns:
        Optional[QuantumCircuit]: A Clifford circuit
    """
    label_inv = str(Clifford(qc_inv).adjoint().to_labels(mode="B"))
    compiled_inverse = cast(dict, clifford_dictionary)[label_inv]
    return compiled_inverse


# pylint: disable=too-many-branches, too-many-statements
def edge_grab(
    qubit_set: List[int] | Sequence[int],
    n_layers: int,
    backend_arg: IQMBackendBase | str,
    density_2q_gates: float = 0.25,
    two_qubit_gate_ensemble: Optional[Dict[str, float]] = None,
    clifford_sqg_probability=1.0,
    sqg_gate_ensemble: Optional[Dict[str, float]] = None,
) -> List[QuantumCircuit]:
    """Generate a list of random layers containing single-qubit Cliffords and two-qubit gates,
    sampled according to the edge-grab algorithm (see arXiv:2204.07568 [quant-ph]).

    Args:
        qubit_set (List[int]): The set of qubits of the backend.
        n_layers (int): The number of layers.
        backend_arg (IQMBackendBase | str): IQM backend.
        density_2q_gates (float): The expected density of 2Q gates in a circuit formed by subsequent application of layers.
                * Default is 0.25
        two_qubit_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 2Q gates, and values being corresponding probabilities.
                * Default is None.
        clifford_sqg_probability (float): Probability with which to uniformly sample Clifford 1Q gates.
                * Default is 1.0.
        sqg_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities.
                * Default is None.
    Raises:
        ValueError: if the probabilities in the gate ensembles do not add up to unity.
    Returns:
        List[QuantumCircuit]: the list of gate layers, in the form of quantum circuits.
    """
    # Check the ensemble of 2Q gates, otherwise assign
    if two_qubit_gate_ensemble is None:
        two_qubit_gate_ensemble = cast(Dict[str, float], {"CZGate": 1.0})
    elif int(sum(two_qubit_gate_ensemble.values())) != 1:
        raise ValueError("The 2Q gate ensemble probabilities must sum to 1.0")

    # Check the ensemble of 1Q gates
    if sqg_gate_ensemble is None:
        if int(clifford_sqg_probability) != 1:
            raise ValueError("If no 1Q gate ensemble is provided, clifford_sqg_probability must be 1.0.")
            # Alternatively, a uniform set of native 1Q rotations could be provided as default with remaining probability
            # Implement later if so wanted
    elif int(sum(sqg_gate_ensemble.values()) + clifford_sqg_probability) != 1:
        raise ValueError("The 1Q gate ensemble probabilities plus clifford_sqg_probability must sum to 1.0.")

    # Validate 1Q gates and get native circuits
    one_qubit_circuits = {"clifford": random_clifford(1).to_circuit()}
    if sqg_gate_ensemble is not None:
        for k in sqg_gate_ensemble.keys():
            one_qubit_circuits[k] = validate_irb_gate(k, backend_arg, gate_params=None)

    # Validate 2Q gates and get native circuits
    two_qubit_circuits = {}
    for k in two_qubit_gate_ensemble.keys():
        two_qubit_circuits[k] = validate_irb_gate(k, backend_arg, gate_params=None)
    # TODO: Admit parametrized 2Q gates! # pylint: disable=fixme

    # Check backend and retrieve if necessary
    if isinstance(backend_arg, str):
        backend = get_iqm_backend(backend_arg)
    else:
        backend = backend_arg

    # Definitions
    num_qubits = len(qubit_set)
    physical_to_virtual_map = {q: i for i, q in enumerate(qubit_set)}

    # Get the possible edges where to place 2Q gates given the backend connectivity
    twoq_edges = []
    for i, q0 in enumerate(qubit_set):
        for q1 in qubit_set[i + 1 :]:
            if (q0, q1) in list(backend.coupling_map):
                twoq_edges.append([q0, q1])
    twoq_edges = list(sorted(twoq_edges))

    # Generate the layers
    layer_list = []
    for _ in range(n_layers):
        # Pick edges at random and store them in a new list "edge_list"
        aux = deepcopy(twoq_edges)
        edge_list = []
        layer = QuantumCircuit(num_qubits)
        # Take (and remove) edges from "aux", then add to "edge_list"
        edge_qubits = []
        while aux:
            new_edge = random.choice(aux)
            edge_list.append(new_edge)
            edge_qubits = list(np.array(edge_list).flatten())
            # Removes all edges which include either of the qubits in new_edge
            aux = [e for e in aux if ((new_edge[0] not in e) and (new_edge[1] not in e))]

        # Define the probability for adding 2Q gates, given the input density
        if len(edge_list) != 0:
            prob_2qgate = num_qubits * density_2q_gates / len(edge_list)
        else:
            prob_2qgate = 0

        # Add gates in selected edges
        for e in edge_list:
            # Sample the 2Q gate
            two_qubit_gate = random.choices(
                list(two_qubit_gate_ensemble.keys()),
                weights=list(two_qubit_gate_ensemble.values()),
                k=1,
            )[0]

            # Pick whether to place the sampled 2Q gate according to the probability above
            is_gate_placed = random.choices(
                [True, False],
                weights=[prob_2qgate, 1 - prob_2qgate],
                k=1,
            )[0]

            if is_gate_placed:
                if two_qubit_gate == "clifford":
                    layer.compose(
                        random_clifford(2).to_instruction(),
                        qubits=[
                            physical_to_virtual_map[e[0]],
                            physical_to_virtual_map[e[1]],
                        ],
                        inplace=True,
                        wrap=False,
                    )
                else:
                    layer.compose(
                        two_qubit_circuits[two_qubit_gate],
                        qubits=[
                            physical_to_virtual_map[e[0]],
                            physical_to_virtual_map[e[1]],
                        ],
                        inplace=True,
                        wrap=False,
                    )
            else:
                # Sample a 1Q gate
                one_qubit_gate = random.choices(
                    list(sqg_gate_ensemble.keys()) + ["clifford"] if sqg_gate_ensemble is not None else ["clifford"],
                    weights=(
                        list(sqg_gate_ensemble.values()) + [clifford_sqg_probability]
                        if sqg_gate_ensemble is not None
                        else [clifford_sqg_probability]
                    ),
                    k=2,
                )
                layer.compose(
                    one_qubit_circuits[one_qubit_gate[0]],
                    qubits=[physical_to_virtual_map[e[0]]],
                    inplace=True,
                )
                layer.compose(
                    one_qubit_circuits[one_qubit_gate[1]],
                    qubits=[physical_to_virtual_map[e[1]]],
                    inplace=True,
                )

        # Add 1Q gates in remaining qubits
        remaining_qubits = [q for q in qubit_set if q not in edge_qubits]
        while remaining_qubits:
            for q in remaining_qubits:
                # Sample the 1Q gate
                one_qubit_gate = random.choices(
                    list(sqg_gate_ensemble.keys()) + ["clifford"] if sqg_gate_ensemble is not None else ["clifford"],
                    weights=(
                        list(sqg_gate_ensemble.values()) + [clifford_sqg_probability]
                        if sqg_gate_ensemble is not None
                        else [clifford_sqg_probability]
                    ),
                    k=1,
                )
                layer.compose(
                    one_qubit_circuits[one_qubit_gate[0]],
                    qubits=[physical_to_virtual_map[q]],
                    inplace=True,
                )
                remaining_qubits.remove(q)

        layer_list.append(layer)

    return layer_list


def estimate_survival_probabilities(num_qubits: int, counts: List[Dict[str, int]]) -> List[float]:
    """Compute a result's probability of being on the ground state.
    Args:
        num_qubits (int): the number of qubits
        counts (List[Dict[str, int]]): the result of the execution of a list of quantum circuits (counts)

    Returns:
        List[float]: the ground state probabilities of the RB sequence
    """
    return [c["0" * num_qubits] / sum(c.values()) if "0" * num_qubits in c.keys() else 0 for c in counts]


def exponential_rb(
    depths: np.ndarray, depolarization_probability: float, offset: float, amplitude: float
) -> np.ndarray:
    """Fit function for interleaved/non-interleaved RB

    Args:
        depths (np.ndarray): the depths of the RB experiment
        depolarization_probability (float): the depolarization value (1-p) of the RB decay
        offset (float): the offset of the RB decay
        amplitude (float): the amplitude of the RB decay

    Returns:
        np.ndarray: the exponential fit function
    """
    return (amplitude - offset) * (1 - depolarization_probability) ** np.array(depths) + offset


def fit_decay_lmfit(
    func: Callable,
    qubit_set: List[int],
    data: List[List[float]] | List[List[List[float]]],
    rb_identifier: str,
    simultaneous_fit_vars: Optional[List[str]] = None,
    interleaved_gate_str: Optional[str] = None,
) -> Tuple[np.ndarray, Parameters]:
    """Perform a fitting routine for 0th-order (Ap^m+B) RB using lmfit

    Args:
        func (Callable): the model function for fitting
        qubit_set (List[int]): the qubits entering the model
        data (List[List[float]] | List[List[List[float]]]): the data to be fitted
        rb_identifier (str): the RB identifier, either "stdrb", "irb" or "mrb"
        simultaneous_fit_vars (List[str], optional): the list of variables used to fit simultaneously
        interleaved_gate_str (Optional[str]): the name of the interleaved gate in IRB
    Returns:
        A tuple of fitting data (list of lists of average fidelities or polarizations) and MRB fit parameters
    """
    n_qubits = len(qubit_set)

    fidelity_guess = 0.99**n_qubits
    offset_guess = 0.3 if n_qubits == 2 else 0.65
    amplitude_guess = 0.7 if n_qubits == 2 else 0.35

    estimates = {
        "depolarization_probability": 2 * (1 - fidelity_guess),
        "offset": offset_guess,
        "amplitude": amplitude_guess + offset_guess,
    }
    # constraints = {
    #     "depolarization_probability": {"min": 0.0, "max": 1.0},
    #     "offset": {"min": 0.0, "max": 1.0},
    #     "amplitude": {"min": 0.0, "max": 1.0},
    # }
    if rb_identifier in ("clifford", "mrb", "drb"):
        fit_data = np.array([np.mean(data, axis=1)])
        if rb_identifier == "clifford":
            params = create_multi_dataset_params(
                func, fit_data, initial_guesses=estimates, constraints=None, simultaneously_fit_vars=None
            )
            params.add(f"p_rb", expr=f"1-depolarization_probability_{1}")
            params.add(f"fidelity_per_clifford", expr=f"p_rb + (1 - p_rb) / (2**{n_qubits})")
            if n_qubits == 1:
                # The construction of the 1Q and 2Q Clifford gate dictionaries in "generate_2qubit_cliffords.ipynb"
                # is based on the reference below; thus the expected amount of 1.875 native gates per Clifford
                # Native gate set being {I, X(pi/2), X(pi), X(-pi/2), Y(pi/2), Y(pi), Y(-pi)} with X(a)=r(a,0), Y(a)=r(a,pi/2)
                # Ref: Barends et al., Nature 508, 500-503 (2014); Eq.(S3) of arXiv:1402.4848 [quant-ph]
                params.add("fidelity_per_native_sqg", expr=f"1 - (1 - (p_rb + (1 - p_rb) / (2**{n_qubits})))/1.875")
        else:
            params = create_multi_dataset_params(
                func,
                fit_data,
                initial_guesses=estimates,
                constraints=None,
                simultaneously_fit_vars=None,
            )
            params.add(f"p_{rb_identifier}", expr=f"1-depolarization_probability_{1}")
            params.add(f"fidelity_{rb_identifier}", expr=f"1 - (1 - p_{rb_identifier}) * (1 - 1 / (4 ** {n_qubits}))")
    else:
        fit_data = np.array([np.mean(data[0], axis=1), np.mean(data[1], axis=1)])
        params = create_multi_dataset_params(
            func,
            fit_data,
            initial_guesses=estimates,
            constraints=None,
            simultaneously_fit_vars=simultaneous_fit_vars,
        )
        params.add(f"p_rb", expr=f"1.0 - depolarization_probability_{1}")
        params.add(f"fidelity_per_clifford", expr=f"p_rb + (1.0 - p_rb) / (2.0**{n_qubits})")
        params.add(f"p_irb", expr=f"1.0 - depolarization_probability_{2}")
        params.add(f"interleaved_fidelity", expr=f"p_irb / p_rb + (1.0 - p_irb / p_rb) / (2.0**{n_qubits})")
        if n_qubits == 1:
            # The construction of the 1Q and 2Q Clifford gate dictionaries in "generate_2qubit_cliffords.ipynb"
            # is based on the reference below; thus the expected amount of 1.875 native gates per Clifford
            # Native gate set being {I, X(pi/2), X(pi), X(-pi/2), Y(pi/2), Y(pi), Y(-pi)} with X(a)=r(a,0), Y(a)=r(a,pi/2)
            # Ref: Barends et al., Nature 508, 500-503 (2014); Eq.(S3) of arXiv:1402.4848 [quant-ph]
            # For IRB it may be used as proxy to how well (or bad) the assumption of uniform fidelity in native sqg gates holds.
            params.add("fidelity_per_native_sqg", expr=f"1.0 - (1.0 - fidelity_per_clifford)/1.875")
        elif n_qubits == 2 and interleaved_gate_str == "CZGate":
            # Here similarly, we may use Eq.(S8 - S11) of arXiv:1402.4848 [quant-ph]
            params.add(f"fidelity_clifford_and_interleaved", expr=f"p_irb + (1.0 - p_irb) / (2.0 ** {n_qubits})")
            params.add(
                "fidelity_per_native_sqg",
                expr=f"(1.0 / 33.0) * (4.0 * fidelity_clifford_and_interleaved - 10.0 * interleaved_fidelity + 39.0)",
            )

    return fit_data, params


@timeit
def generate_all_rb_circuits(
    qubits: List[int],
    sequence_lengths: List[int],
    clifford_dict: Dict[str, QuantumCircuit],
    num_circuit_samples: int,
    backend_arg: str | IQMBackendBase,
    interleaved_gate: Optional[QuantumCircuit],
) -> Tuple[Dict[int, List[QuantumCircuit]], Dict[int, List[QuantumCircuit]]]:
    """
    Args:
        qubits (List[int]): List of qubits
        sequence_lengths (List[int]): List of sequence lengths
        clifford_dict (Dict[str, QuantumCircuit]): the dictionary of Clifford circuits
        num_circuit_samples (int): the number of circuits samples
        backend_arg (str | IQMBackendBase): the backend fir which to generate the circuits.
        interleaved_gate (str): the name of the interleaved gate
    Returns:
        Tuple of untranspiled and transpiled circuits for all class-defined sequence lengths
    """
    untranspiled = {}
    transpiled = {}
    for s in sequence_lengths:
        qcvv_logger.info(f"Now at sequence length {s}")
        untranspiled[s], transpiled[s] = generate_random_clifford_seq_circuits(
            qubits, clifford_dict, s, num_circuit_samples, backend_arg, interleaved_gate
        )
    return untranspiled, transpiled


# pylint: disable=too-many-branches, disable=too-many-statements
@timeit
def generate_fixed_depth_parallel_rb_circuits(
    qubits_array: List[List[int]],
    cliffords_1q: Dict[str, QuantumCircuit],
    cliffords_2q: Dict[str, QuantumCircuit],
    sequence_length: int,
    num_samples: int,
    backend_arg: IQMBackendBase | str,
    interleaved_gate: Optional[QuantumCircuit] = None,
) -> Tuple[List[QuantumCircuit], List[QuantumCircuit]]:
    """Generates parallel RB circuits, before and after transpilation, at fixed depth

    Args:
        qubits_array (List[List[int]]): the qubits entering the quantum circuits.
        cliffords_1q (Dict[str, QuantumCircuit]): dictionary of 1-qubit Cliffords in terms of IQM-native r gates.
        cliffords_2q (Dict[str, QuantumCircuit]): dictionary of 2-qubit Cliffords in terms of IQM-native r and CZ gates.
        sequence_length (int): the number of random Cliffords in the circuits.
        num_samples (int): the number of circuit samples.
        backend_arg (IQMBackendBase | str): the backend to transpile the circuits to.
        interleaved_gate (Optional[QuantumCircuit]): whether the circuits should have interleaved gates.
    Returns:
        A list of QuantumCircuits of given RB sequence length for parallel RB
    """

    if isinstance(backend_arg, str):
        backend = get_iqm_backend(backend_arg)
    else:
        backend = backend_arg

    # Identify total amount of qubits
    qubit_counts = [len(x) for x in qubits_array]

    # Shuffle qubits_array: we don't want unnecessary qubit registers
    shuffled_qubits_array = relabel_qubits_array_from_zero(qubits_array)
    # The total amount of qubits the circuits will have
    n_qubits = sum(qubit_counts)

    # Get the keys of the Clifford dictionaries
    clifford_1q_keys = list(cliffords_1q.keys())
    clifford_2q_keys = list(cliffords_2q.keys())

    # Generate the circuit samples
    circuits_list: List[QuantumCircuit] = []
    circuits_transpiled_list: List[QuantumCircuit] = []
    for _ in range(num_samples):
        circuit = QuantumCircuit(n_qubits)
        # Need to track inverses on each qubit, or each pair of qubits, separately
        circ_inverses = [QuantumCircuit(n) for n in qubit_counts]
        # Place Clifford sequences on each
        for _ in range(sequence_length):
            # Sample the random Cliffords for each qubit or qubits
            cliffords = []
            for n in qubit_counts:
                if n == 1:
                    rand_key = random.choice(clifford_1q_keys)
                    c_1q = cast(dict, cliffords_1q)[rand_key]
                    cliffords.append(c_1q)
                else:
                    rand_key = random.choice(clifford_2q_keys)
                    c_2q = cast(dict, cliffords_2q)[rand_key]
                    cliffords.append(c_2q)
            # Compose the sampled Cliffords in the circuit and add barrier
            for n, shuffled_qubits in enumerate(shuffled_qubits_array):
                circuit.compose(cliffords[n], qubits=shuffled_qubits, inplace=True)
                circ_inverses[n].compose(cliffords[n], qubits=list(range(qubit_counts[n])), inplace=True)
            circuit.barrier()  # NB: mind the barriers!

            if interleaved_gate is not None:
                for n, shuffled_qubits in enumerate(shuffled_qubits_array):
                    circuit.compose(interleaved_gate, qubits=shuffled_qubits, inplace=True)
                    circ_inverses[n].compose(interleaved_gate, qubits=list(range(qubit_counts[n])), inplace=True)
                circuit.barrier()

        # Compile and compose the inverse
        # compiled_inverse_clifford = []
        for n, shuffled_qubits in enumerate(shuffled_qubits_array):
            clifford_dict = cliffords_1q if qubit_counts[n] == 1 else cliffords_2q
            circuit.compose(
                compute_inverse_clifford(circ_inverses[n], clifford_dict),
                qubits=shuffled_qubits,
                inplace=True,
            )
        # Add measurement
        circuit.measure_all()

        circuits_list.append(circuit)
        # Transpilation here only means to the layout - avoid using automated transpilers!
        circuit_transpiled = QuantumCircuit(backend.num_qubits)
        qubits_array_flat = [x for y in qubits_array for x in y]
        circuit_transpiled.compose(circuit, qubits=qubits_array_flat, inplace=True)
        circuits_transpiled_list.append(circuit_transpiled)

    return circuits_list, circuits_transpiled_list


def generate_random_clifford_seq_circuits(
    qubits: List[int],
    clifford_dict: Dict[str, QuantumCircuit],
    seq_length: int,
    num_circ_samples: int,
    backend_arg: str | IQMBackendBase,
    interleaved_gate: Optional[QuantumCircuit] = None,
) -> Tuple[List[QuantumCircuit], List[QuantumCircuit]]:
    """Generate random Clifford circuits in native gates for a given sequence length.

    Args:
        qubits (List[int]): the list of qubits
        clifford_dict (Dict[str, QuantumCircuit]): A dictionary of Clifford gates labeled by (de)stabilizers
        seq_length (int): the sequence length
        num_circ_samples (int): the number of samples
        backend_arg (str | IQMBackendBase):
        interleaved_gate (Optional[QuantumCircuit]): Clifford native gate to be interleaved - None by default
    Returns:
        List[QuantumCircuit]: the list of `self.num_samples` random Clifford quantum circuits
    """
    if isinstance(backend_arg, str):
        backend = get_iqm_backend(backend_arg)
    else:
        backend = backend_arg

    qc_list = []  # List of random Clifford circuits
    qc_list_transpiled = []
    num_qubits = len(qubits)
    logic_qubits = list(range(num_qubits))

    if num_qubits > 2:
        raise ValueError("Please specify qubit layouts with only n=1 or n=2 qubits. Run MRB for n>2 instead.")

    clifford_keys = []
    if clifford_dict is not None:
        clifford_keys = list(clifford_dict.keys())

    for _ in range(num_circ_samples):
        qc = QuantumCircuit(num_qubits)
        qc_inv = QuantumCircuit(num_qubits)
        # Compose circuit with random Clifford gates
        for _ in range(seq_length):
            rand_key = random.choice(clifford_keys)
            clifford = cast(dict, clifford_dict)[rand_key]
            # Append clifford
            qc.compose(clifford, qubits=logic_qubits, inplace=True)
            # Append clifford gate to circuit to invert
            qc_inv.compose(clifford, qubits=logic_qubits, inplace=True)
            qc.barrier()
            # Append interleaved if not None
            if interleaved_gate is not None:
                qc.compose(interleaved_gate, qubits=logic_qubits, inplace=True)
                qc_inv.compose(interleaved_gate, qubits=logic_qubits, inplace=True)
                qc.barrier()
        # Append the inverse
        qc.compose(
            compute_inverse_clifford(qc_inv, clifford_dict),
            qubits=logic_qubits,
            inplace=True,
        )
        qc.measure_all()

        qc_list.append(qc)
        qc_transpiled = QuantumCircuit(backend.num_qubits)
        qc_transpiled.compose(qc, qubits=qubits, inplace=True)
        qc_list_transpiled.append(qc_transpiled)

    return qc_list, qc_list_transpiled


def get_survival_probabilities(num_qubits: int, counts: List[Dict[str, int]]) -> List[float]:
    """Compute a result's probability of being on the ground state.

    Args:
        num_qubits (int): the number of qubits
        counts (List[Dict[str, int]]): the result of the execution of a list of quantum circuits (counts)

    Returns:
        List[float]: the ground state probabilities of the RB sequence
    """
    return [c["0" * num_qubits] / sum(c.values()) if "0" * num_qubits in c.keys() else 0 for c in counts]


def import_native_gate_cliffords(
    system_size: Optional[str] = None,
) -> Dict[str, QuantumCircuit] | Tuple[Dict[str, QuantumCircuit], Dict[str, QuantumCircuit]]:
    """Import native gate Clifford dictionaries

    Args:
        system_size (str, optional): System size to load, either "1q" or "2q". If None, load both dictionaries.

    Returns:
        If system_size is specified, returns the dictionary for that system size.
        If system_size is None, returns a tuple of (1q_dict, 2q_dict).

    Raises:
        ValueError: If system_size is not None, "1q", or "2q".
    """
    if system_size is not None and system_size not in ["1q", "2q"]:
        raise ValueError('system_size must be either "1q", "2q", or None')

    clifford_1q_dict = {}
    clifford_2q_dict = {}

    if system_size is None or system_size == "1q":
        with open(os.path.join(os.path.dirname(__file__), "clifford_1q.pkl"), "rb") as f1q:
            clifford_1q_dict = pickle.load(f1q)

    if system_size is None or system_size == "2q":
        with open(os.path.join(os.path.dirname(__file__), "clifford_2q.pkl"), "rb") as f2q:
            clifford_2q_dict = pickle.load(f2q)

    qcvv_logger.info(f"Clifford dictionaries for {system_size or 'both 1 & 2 qubits'} imported successfully!")

    if system_size == "1q":
        return clifford_1q_dict
    if system_size == "2q":
        return clifford_2q_dict

    return clifford_1q_dict, clifford_2q_dict


def lmfit_minimizer(
    fit_parameters: Parameters, fit_data: np.ndarray, depths: List[int], func: Callable
) -> MinimizerResult:
    """
    Args:
        fit_parameters (Parameters): the parameters to fit
        fit_data (np.ndarray): the data to fit
        depths (List[int]): the depths of the RB experiment
        func (Callable): the model function for fitting
    Returns:
        MinimizerResult: the result of the minimization
    """
    return minimize(
        fcn=multi_dataset_residual,
        params=fit_parameters,
        args=(depths, fit_data, func),
    )


def relabel_qubits_array_from_zero(
    arr: List[List[int]], separate_registers: bool = False, reversed_arr: bool = False
) -> List[List[int]]:
    """Helper function to relabel a qubits array to an increasingly ordered one starting from zero
    e.g., [[2,3], [5], [7,8]]  ->  [[0,1], [2], [3,4]]
    Note: this assumes the input array is sorted in increasing order!

    Args:
        arr (List[List[int]]): the qubits array to relabel.
        separate_registers (bool): whether the clbits were generated in separate registers.
                * This has the effect of skipping one value in between each sublist, e.g., [[2,3], [5], [7,8]]  ->  [[0,1], [3], [5,6]]
                * Default is False.
        reversed_arr (bool): whether the input array is reversed.
                * This has the effect of reversing the output array, e.g., [[2,3], [5,7], [8]] -> [[0], [1,2], [3,4]]
                * Default is False.

    Returns:
        List[List[int]]: the relabeled qubits array.
    """
    # Flatten the original array
    flat_list = [item for sublist in arr for item in sublist]
    # Generate a list of ordered numbers with the same length as the flattened array
    # If separate_registers is True, ordered_indices has to skip one value in between each sublist (as if the clbits were generated in separate registers)
    # e.g. [[2,3], [5], [7,8]] -> [[0,1],[3],[5,6]] if separate_registers=True
    ordered_indices = list(range(len(flat_list) + len(arr) - 1)) if separate_registers else list(range(len(flat_list)))
    # Reconstruct the list of lists structure
    result = []
    index = 0
    for sublist in reversed(arr) if reversed_arr else arr:
        result.append(ordered_indices[index : index + len(sublist)])
        index += len(sublist) + 1 if separate_registers else len(sublist)
    return result


def submit_parallel_rb_job(
    backend_arg: IQMBackendBase,
    qubits_array: Sequence[Sequence[int]],
    depth: int,
    sorted_transpiled_circuit_dicts: Dict[Tuple[int, ...], List[QuantumCircuit]],
    shots: int,
    calset_id: Optional[str],
    max_gates_per_batch: Optional[str],
    max_circuits_per_batch: Optional[int],
) -> Dict[str, Any]:
    """Submit fixed-depth parallel MRB jobs for execution in the specified IQMBackend
    Args:
        backend_arg (IQMBackendBase): the IQM backend to submit the job
        qubits_array (Sequence[Sequence[int]]): the qubits to identify the submitted job
        depth (int): the depth (number of canonical layers) of the circuits to identify the submitted job
        sorted_transpiled_circuit_dicts (Dict[Tuple[int,...], List[QuantumCircuit]]): A dictionary containing all MRB circuits
        shots (int): the number of shots to submit the job
        calset_id (Optional[str]): the calibration identifier
        max_gates_per_batch (Optional[str]): the maximum number of gates per batch to submit the job
        max_circuits_per_batch (Optional[int]): the maximum number of circuits per batch to submit the job.
    Returns:
        Dict with qubit layout, submitted job objects, type (vanilla/DD) and submission time
    """
    # Submit
    # Send to execute on backend
    # pylint: disable=unbalanced-tuple-unpacking
    execution_jobs, time_submit = submit_execute(
        sorted_transpiled_circuit_dicts,
        backend_arg,
        shots,
        calset_id,
        max_gates_per_batch=max_gates_per_batch,
        max_circuits_per_batch=max_circuits_per_batch,
    )
    rb_submit_results = {
        "qubits": qubits_array,
        "depth": depth,
        "jobs": execution_jobs,
        "time_submit": time_submit,
    }
    return rb_submit_results


def submit_sequential_rb_jobs(
    qubits: List[int],
    transpiled_circuits: Dict[int, List[QuantumCircuit]],
    shots: int,
    backend_arg: str | IQMBackendBase,
    calset_id: Optional[str] = None,
    max_gates_per_batch: Optional[int] = None,
    max_circuits_per_batch: Optional[int] = None,
    circuit_compilation_options: Optional[CircuitCompilationOptions] = None,
) -> List[Dict[str, Any]]:
    """Submit sequential RB jobs for execution in the specified IQMBackend
    Args:
        qubits (List[int]): the qubits to identify the submitted job
        transpiled_circuits (Dict[str, List[QuantumCircuit]]): A dictionary containing all MRB circuits
        shots (int): the number of shots to submit per job
        backend_arg (IQMBackendBase): the IQM backend to submit the job
        calset_id (Optional[str]): the calibration identifier
        max_gates_per_batch (Optional[int]): the maximum number of gates per batch
        max_circuits_per_batch (Optional[int]): the maximum number of circuits per batch
        circuit_compilation_options (Optional[CircuitCompilationOptions]): Compilation options passed to submit_execute
    Returns:
        Dict with qubit layout, submitted job objects, type (vanilla/DD) and submission time
    """
    if isinstance(backend_arg, str):
        backend = get_iqm_backend(backend_arg)
    else:
        backend = backend_arg

    all_submit_results = []
    rb_submit_results = {}
    for depth in transpiled_circuits.keys():
        # Submit - send to execute on backend
        # pylint: disable=unbalanced-tuple-unpacking
        execution_jobs, time_submit = submit_execute(
            {tuple(qubits): transpiled_circuits[depth]},
            backend,
            shots,
            calset_id,
            max_gates_per_batch,
            max_circuits_per_batch=max_circuits_per_batch,
            circuit_compilation_options=circuit_compilation_options,
        )
        rb_submit_results[depth] = {
            "qubits": qubits,
            "depth": depth,
            "jobs": execution_jobs,
            "time_submit": time_submit,
        }
        all_submit_results.append(rb_submit_results[depth])

    return all_submit_results


def survival_probabilities_parallel(
    qubits_array: List[List[int]], counts: List[Dict[str, int]], separate_registers: bool = False
) -> Dict[str, List[float]]:
    """
    Estimates marginalized survival probabilities from a parallel RB execution (at fixed depth).

    Args:
        qubits_array (List[int]): List of qubits in which the experiment was performed
        counts (Dict[str, int]): The measurement counts for corresponding bitstrings
        separate_registers (bool): Whether the clbits were generated in separate registers
            * If True, the bit strings will be separated by a space, e.g., '00 10' means '00' belongs to one register and '10' to another.
            * Default is False.

    Returns:
        Dict[str, List[float]]: The survival probabilities for each qubit.

    """
    # Global probability estimations
    global_probabilities = [{k: v / sum(c.values()) for k, v in c.items()} for c in counts]

    all_bit_indices = relabel_qubits_array_from_zero(
        qubits_array, separate_registers=separate_registers, reversed_arr=True
    )  # Need reversed_arr because count bitstrings get reversed!

    # Estimate all marginal probabilities
    marginal_probabilities: Dict[str, List[Dict[str, float]]] = {str(q): [] for q in qubits_array}
    for position, indices in reversed(list(enumerate(all_bit_indices))):
        marginal_probabilities[str(qubits_array[len(all_bit_indices) - 1 - position])] = [
            marginal_distribution(global_probability, indices) for global_probability in global_probabilities
        ]

    # Estimate the survival probabilities in the marginal distributions
    marginal_survival_probabilities: Dict[str, List[float]] = {str(q): [] for q in qubits_array}
    for q in qubits_array:
        n_qubits = len(q)
        marginal_survival_probabilities[str(q)] = [
            c["0" * n_qubits] / sum(c.values()) if "0" * n_qubits in c.keys() else 0
            for c in marginal_probabilities[str(q)]
        ]

    return marginal_survival_probabilities


# pylint: disable=too-many-statements
def plot_rb_decay(
    identifier: str,
    qubits_array: List[List[int]],
    dataset: xr.Dataset,
    observations: Dict[int, Dict[str, Any]],
    violin: bool = True,
    scatter: bool = True,
    bars: bool = False,
    shade_stdev: bool = False,
    shade_meanerror: bool = False,
    logscale: bool = True,
    interleaved_gate: Optional[str] = None,
    mrb_2q_density: Optional[float | Dict[str, float]] = None,
    mrb_2q_ensemble: Optional[Dict[str, Dict[str, float]]] = None,
    is_eplg: bool = False,
) -> Tuple[str, Figure]:
    """Plot the fidelity decay and the fit to the model.

    Args:
        identifier (str): the type of RB experiment
        qubits_array (List[List[int]]): Array of sets of qubits for which to plot decays
        dataset (xr.dataset): the dataset from the experiment
        observations (Dict[str, Dict[str, Any]]): the corresponding observations from the experiment
        bars (bool, optional): Whether error bars are plotted or not. Defaults to False
        violin (bool, optional): Whether violins are plotted or not. Defaults to True
        scatter (bool, optional): Whether all individual points are plotted or not. Defaults to True
        shade_stdev (bool, optional): Whether standard deviations are shaded or not. Defaults to False
        shade_meanerror (bool, optional): Whether to shade standard deviations. Defaults to False
        logscale (bool, optional): Whether x-axis uses logscale. Defaults to True
        interleaved_gate (Optional[str]): The label or the interleaved gate. Defaults to None
        mrb_2q_density (Optional[float], optional): Density of MRB 2Q gates. Defaults to None.
        mrb_2q_ensemble (Optional[Dict[str, float]], optional): MRB ensemble of 2Q gates. Defaults to None.
        is_eplg (bool, optional): Whether the experiment is EPLG or not. Defaults to False.

    Returns:
        Tuple[str, Figure]: the plot title and the figure
    """
    fig, ax = plt.subplots()

    cmap = plt.get_cmap("winter")

    num_circuit_samples = dataset.attrs["num_circuit_samples"]
    timestamp = dataset.attrs["execution_timestamp"]
    backend_name = dataset.attrs["backend_name"]
    # If only one layout is passed, the index to retrieve results must be shifted!
    qubits_index = 0
    dataset_attrs = dataset.attrs
    if len(qubits_array) == 1:
        config_qubits_array = dataset.attrs["qubits_array"]
        if isinstance(config_qubits_array[0][0], int):
            qubits_index = config_qubits_array.index(qubits_array[0])
            # dataset_attrs = dataset.attrs
        else:
            # Find the subarray that contains the qubits_array
            for c_idx, c in enumerate(config_qubits_array):
                if qubits_array[0] in c:
                    group_idx = c_idx
                    qubits_index = c.index(qubits_array[0])
                    dataset_attrs = dataset.attrs[group_idx]
            # flat_config_qubits_array = [item for sublist in config_qubits_array for item in sublist]
            # qubits_index = flat_config_qubits_array.index(qubits_array[0])

    # Fetch the relevant observations indexed by qubit layouts
    depths = {}
    polarizations = {}
    average_polarizations = {}
    stddevs_from_mean = {}
    fidelity_value = {}
    fidelity_stderr = {}
    fidelity_native1q_value = {}
    fidelity_native1q_stderr = {}
    decay_rate = {}
    offset = {}
    amplitude = {}
    rb_type_keys = []
    colors = []
    if identifier != "irb":
        rb_type_keys = [identifier]
        colors = [cmap(i) for i in np.linspace(start=1, stop=0, num=len(qubits_array)).tolist()]
        if identifier in ("mrb", "drb"):
            depths[identifier] = {
                str(q): list(dataset_attrs[q_idx]["polarizations"].keys())
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            polarizations[identifier] = {
                str(q): dataset_attrs[q_idx]["polarizations"] for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            average_polarizations[identifier] = {
                str(q): dataset_attrs[q_idx]["average_polarization_nominal_values"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            stddevs_from_mean[identifier] = {
                str(q): dataset_attrs[q_idx]["average_polarization_stderr"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
        else:  # identifier == "clifford"
            depths[identifier] = {
                str(q): list(dataset_attrs[q_idx]["fidelities"].keys())
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            polarizations[identifier] = {
                str(q): dataset_attrs[q_idx]["fidelities"] for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            average_polarizations[identifier] = {
                str(q): dataset_attrs[q_idx]["average_fidelities_nominal_values"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            stddevs_from_mean[identifier] = {
                str(q): dataset_attrs[q_idx]["average_fidelities_stderr"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            fidelity_native1q_value[identifier] = {
                str(q): observations[q_idx]["average_native_gate_fidelity"]["value"] if len(q) == 1 else np.nan
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            fidelity_native1q_stderr[identifier] = {
                str(q): observations[q_idx]["average_native_gate_fidelity"]["uncertainty"] if len(q) == 1 else np.nan
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
        # These are common to both MRB and standard Clifford
        fidelity_value[identifier] = {
            str(q): observations[q_idx]["average_gate_fidelity"]["value"]
            for q_idx, q in enumerate(qubits_array, qubits_index)
        }
        fidelity_stderr[identifier] = {
            str(q): observations[q_idx]["average_gate_fidelity"]["uncertainty"]
            for q_idx, q in enumerate(qubits_array, qubits_index)
        }
        decay_rate[identifier] = {
            str(q): dataset_attrs[q_idx]["decay_rate"]["value"] for q_idx, q in enumerate(qubits_array, qubits_index)
        }
        offset[identifier] = {
            str(q): dataset_attrs[q_idx]["fit_offset"]["value"] for q_idx, q in enumerate(qubits_array, qubits_index)
        }
        amplitude[identifier] = {
            str(q): dataset_attrs[q_idx]["fit_amplitude"]["value"] for q_idx, q in enumerate(qubits_array, qubits_index)
        }
    else:  # id IRB
        rb_type_keys = list(observations[0].keys())
        colors = [cmap(i) for i in np.linspace(start=1, stop=0, num=len(rb_type_keys)).tolist()]
        for rb_type in rb_type_keys:
            depths[rb_type] = {
                str(q): list(dataset_attrs[q_idx][rb_type]["fidelities"].keys())
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            polarizations[rb_type] = {
                str(q): dataset_attrs[q_idx][rb_type]["fidelities"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            average_polarizations[rb_type] = {
                str(q): dataset_attrs[q_idx][rb_type]["average_fidelities_nominal_values"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            stddevs_from_mean[rb_type] = {
                str(q): dataset_attrs[q_idx][rb_type]["average_fidelities_stderr"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            fidelity_value[rb_type] = {
                str(q): observations[q_idx][rb_type]["average_gate_fidelity"]["value"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            fidelity_stderr[rb_type] = {
                str(q): observations[q_idx][rb_type]["average_gate_fidelity"]["uncertainty"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            decay_rate[rb_type] = {
                str(q): dataset_attrs[q_idx][rb_type]["decay_rate"]["value"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            offset[rb_type] = {
                str(q): dataset_attrs[q_idx][rb_type]["fit_offset"]["value"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }
            amplitude[rb_type] = {
                str(q): dataset_attrs[q_idx][rb_type]["fit_amplitude"]["value"]
                for q_idx, q in enumerate(qubits_array, qubits_index)
            }

    for index_irb, key in enumerate(rb_type_keys):
        for index_qubits, qubits in enumerate(qubits_array):
            # Index for colors
            index = index_irb if identifier == "irb" else index_qubits
            # Plot Averages
            # Draw the averages (w or w/o error bars)
            if bars:
                y_err_f = stddevs_from_mean[key][str(qubits)]
            else:
                y_err_f = None
            ax.errorbar(
                depths[key][str(qubits)],
                average_polarizations[key][str(qubits)].values(),
                yerr=y_err_f,
                # label=f"Avg with {num_circ_samples} samples",
                capsize=4,
                color=colors[index],
                fmt="o",
                mec="black",
                alpha=1,
                markersize=5,
            )
            if shade_stdev:
                # Shade the standard deviation
                ax.fill_between(
                    depths[key][str(qubits)],
                    [
                        a - np.sqrt(num_circuit_samples) * b
                        for a, b in zip(
                            average_polarizations[key][str(qubits)].values(),
                            stddevs_from_mean[key][str(qubits)].values(),
                        )
                    ],
                    [
                        a + np.sqrt(num_circuit_samples) * b
                        for a, b in zip(
                            average_polarizations[key][str(qubits)].values(),
                            stddevs_from_mean[key][str(qubits)].values(),
                        )
                    ],
                    color=colors[index],
                    alpha=0.2,
                    interpolate=True,
                )
            if shade_meanerror:
                # Shade the error from the mean
                ax.fill_between(
                    depths[key][str(qubits)],
                    [
                        a - b
                        for a, b in zip(
                            average_polarizations[key][str(qubits)].values(),
                            stddevs_from_mean[key][str(qubits)].values(),
                        )
                    ],
                    [
                        a + b
                        for a, b in zip(
                            average_polarizations[key][str(qubits)].values(),
                            stddevs_from_mean[key][str(qubits)].values(),
                        )
                    ],
                    color=colors[index],
                    alpha=0.1,
                    interpolate=True,
                )
            if violin:
                widths = [0.5 * m for m in depths[key][str(qubits)]]
                violin_parts_f = ax.violinplot(
                    polarizations[key][str(qubits)].values(),
                    positions=depths[key][str(qubits)],
                    showmeans=False,
                    showextrema=False,
                    widths=widths,
                )
                assert isinstance(violin_parts_f["bodies"], list)
                for pc in violin_parts_f["bodies"]:
                    assert isinstance(pc, PolyCollection)
                    pc.set_facecolor(colors[index])
                    pc.set_edgecolor("g")
                    pc.set_alpha(0.1)
            if scatter:
                # Plot the individual outcomes
                flat_fidelity_data = list(chain.from_iterable(polarizations[key][str(qubits)].values()))
                scatter_x = [
                    [depth] * len(polarizations[key][str(qubits)][depth]) for depth in depths[key][str(qubits)]
                ]
                flat_scatter_x = list(chain.from_iterable(scatter_x))
                ax.scatter(
                    flat_scatter_x,
                    flat_fidelity_data,
                    s=3,
                    color=colors[index],
                    alpha=0.35,
                )
            # Define the points of the x-axis
            x_linspace = np.linspace(np.min(depths[key][str(qubits)]), np.max(depths[key][str(qubits)]), 300)
            # Calculate the fit points of the y-axis
            y_fit = exponential_rb(
                x_linspace,
                1 - decay_rate[key][str(qubits)],
                offset[key][str(qubits)],
                amplitude[key][str(qubits)],
            )
            # Plot
            # Handle None types in instances where fidelity or stderr were not set
            if fidelity_value[key][str(qubits)] is None:
                fidelity_value[key][str(qubits)] = np.nan
            if fidelity_stderr[key][str(qubits)] is None:
                fidelity_stderr[key][str(qubits)] = np.nan

            if identifier in ("mrb", "drb"):
                plot_label = fr"$\overline{{F}}_{{{identifier.upper()}}} (n={len(qubits)})$ = {100.0 * fidelity_value[key][str(qubits)]:.2f} +/- {100.0 * fidelity_stderr[key][str(qubits)]:.2f} (%)"
            elif key == "interleaved":
                plot_label = fr"$\overline{{F}}_{{{interleaved_gate}}}$ = {100.0 * fidelity_value[key][str(qubits)]:.2f} +/- {100.0 * fidelity_stderr[key][str(qubits)]:.2f} (%)"
            else:  # if id is "clifford"
                if len(qubits) == 1 and identifier != "irb":
                    plot_label = fr"$\overline{{F}}_{{native\_sqg}} \simeq$ {100.0 * fidelity_native1q_value[key][str(qubits)]:.2f} +/- {100.0 * fidelity_native1q_stderr[key][str(qubits)]:.2f} (%)"
                else:
                    plot_label = fr"$\overline{{F}}_{{CRB}}$ = {100.0 * fidelity_value[key][str(qubits)]:.2f} +/- {100.0 * fidelity_stderr[key][str(qubits)]:.2f} (%)"

            ax.plot(
                x_linspace,
                y_fit,
                color=colors[index],
                alpha=0.5,
                label=plot_label,
            )

    # Labels
    on_qubits = "on all qubit layouts"
    fig_name = "all_qubit_layouts"
    if len(qubits_array) == 1:
        on_qubits = f"on qubits {qubits_array[0]}"
        fig_name = f"{str(qubits_array[0])}"

    if identifier == "irb":
        ax.set_title(
            f"{identifier.upper()} experiment for {interleaved_gate} {on_qubits}\nbackend: {backend_name} --- {timestamp}"
        )
    elif identifier == "clifford":
        ax.set_title(f"{identifier.capitalize()} experiment {on_qubits}\nbackend: {backend_name} --- {timestamp}")
    else:
        if not is_eplg:
            if identifier == "drb" and len(qubits_array) == 1:
                density = cast(dict, mrb_2q_density)[str(qubits_array[0])]
                ensemble = cast(dict, mrb_2q_ensemble)[str(qubits_array[0])]
            else:
                density = mrb_2q_density
                ensemble = mrb_2q_ensemble
            ax.set_title(
                f"{identifier.upper()} experiment {on_qubits}\n"
                f"2Q gate density: {density}, ensemble {ensemble}\n"
                f"backend: {backend_name} --- {timestamp}"
            )
        else:
            ax.set_title(
                f"EPLG parallel {identifier.upper()} experiment {on_qubits}\n"
                f"backend: {backend_name} --- {timestamp}"
            )

    if identifier in ("mrb", "drb"):
        ax.set_ylabel("Polarization")
        ax.set_xlabel("Layer Depth")
    else:
        ax.set_ylabel("Fidelity")
        ax.set_xlabel("Sequence Length")
    if logscale:
        ax.set_xscale("log")

    # Show the relevant depths!
    # Gather and flatten all the possible depths and then pick unique elements
    all_depths = [x for d in depths.values() for w in d.values() for x in w]

    xticks = sorted(list(set(all_depths)))
    ax.set_xticks(xticks, labels=xticks, rotation=45)

    plt.legend(fontsize=8)
    ax.grid()

    plt.close()

    return fig_name, fig


def validate_rb_qubits(qubits_array: List[List[int]], backend_arg: str | IQMBackendBase):
    """Validate qubit inputs for a Clifford RB experiment
    Args:
        qubits_array (List[List[int]]): the array of qubits
        backend_arg (IQMBackendBase): the IQM backend
    Raises:
        ValueError if specified pairs of qubits are not connected
    """
    if isinstance(backend_arg, str):
        backend = get_iqm_backend(backend_arg)
    else:
        backend = backend_arg
    # Identify total amount of qubits
    qubit_counts = [len(x) for x in qubits_array]

    # Validations
    # Suggest MRB for n>2 qubits
    if any(n > 2 for n in qubit_counts):
        raise ValueError("Please specify qubit layouts with only n=1 or n=2 qubits. Run MRB for n>2 instead.")
    pairs_qubits = [qubits_array[i] for i, n in enumerate(qubit_counts) if n == 2]
    # Qubits should be connected
    for x in pairs_qubits:
        if tuple(x) not in list(backend.coupling_map) and tuple(reversed(x)) not in list(backend.coupling_map):
            raise ValueError(f"Input qubits {tuple(x)} are not connected")


def validate_irb_gate(
    gate_id: str,
    backend_arg: str | IQMBackendBase,
    gate_params: Optional[List[float]] = None,
) -> QuantumCircuit:
    """Validate that an input gate is Clifford and transpiled to IQM's native basis

    Args:
        gate_id (str): the gate identifier as a Qiskit circuit library operator
        backend_arg (IQMBackendBase): the IQM backend to verify transpilation
        gate_params (Optional[List[float]]): the gate parameters
    Returns:
        Transpiled circuit

    """
    if gate_params is not None:
        gate = getattr(import_module("qiskit.circuit.library"), gate_id)(*gate_params)
    else:
        gate = getattr(import_module("qiskit.circuit.library"), gate_id)()

    if isinstance(backend_arg, str):
        backend = get_iqm_backend(backend_arg)
    else:
        backend = backend_arg

    qc = QuantumCircuit(gate.num_qubits)
    if gate in backend.operation_names:
        qc.compose(gate, qubits=range(gate.num_qubits), inplace=True)
        return qc

    # else transpile
    qc.compose(gate, qubits=range(gate.num_qubits), inplace=True)
    # Use Optimize SQG but retain final r gate - want the unitary to be preserved!
    qc_t = optimize_single_qubit_gates(
        transpile(qc, basis_gates=backend.operation_names, optimization_level=3), drop_final_rz=False
    )
    return qc_t
