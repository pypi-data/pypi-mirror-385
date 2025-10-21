"""
Bridge between mGST and Qiskit
"""

import random

import numpy as np
from qiskit.circuit.library import IGate
from qiskit.quantum_info import Operator

from iqm.qiskit_iqm import IQMCircuit as QuantumCircuit
from mGST import low_level_jit


def qiskit_gate_to_operator(gate_set):
    """Convert a set of Qiskit gates to their unitary operators.

    This function takes a list of Qiskit gate objects and them into operators, returned as a NumPy
    array of matrices.

    Parameters
    ----------
    gate_set : list
        A list of Qiskit gate objects. Each gate in the list is converted to its
        corresponding unitary.

    Returns
    -------
    numpy.ndarray
        An array of process matrices. Each element in the array is a 2D NumPy array.
    """
    return np.array([[Operator(gate).reverse_qargs().to_matrix()] for gate in gate_set])


def add_idle_gates(gate_set, active_qubits, gate_qubits):
    """Add additional idle gates to a gate set
    Each gate in the output gate_set acts on exactly the number of qubits
    on which the GST experiment ist defined. For instance if the GST
    experiment is supposed to be run on qubits [0,1,2], then a X-Gate
    on the 0-th qubit turns into X otimes Idle otimes Idle.
    This representation is needed for the internal handling in mGST.

    Parameters
    ----------
    gate_set : list of Qiskit Circuits
        Each element is a gate to be used for GST, stored as a circuit.
    active_qubits : list integers
        Specifies the list of qubits on which GST-circuits are run.
    gate_qubits : list of lists of integers
        The i-th elements in the active_qubit list specifies on which qubits
        the original i-th gate in the input gate set is supposed to act.
    Returns
    -------
    gate_set : list of Qiskit Circuits
        The output gate set with added idle gates.
    """
    d = len(gate_qubits)
    for i in range(d):
        idle_qubits = active_qubits.copy()
        for j in gate_qubits[i]:
            idle_qubits.remove(j)
        if idle_qubits:
            for l in idle_qubits:
                gate_set[i].append(IGate(), [l])
    return gate_set


def remove_idle_wires(qc):
    """Removes all wires on which no gate acts
    Credit to: https://quantumcomputing.stackexchange.com/a/37192
    This shrinks the circuit for the conversion to quantum channels.

    Parameters
    ----------
    qc  Qiskit quantum circuit

    Returns
    -------
    qc_out Qiskit quantum circuit
        The circuit with idle wires removed.
    """
    qc_out = qc.copy()
    gate_count = {qubit: 0 for qubit in qc.qubits}
    for gate in qc.data:
        for qubit in gate.qubits:
            gate_count[qubit] += 1
    for qubit, count in gate_count.items():
        if count == 0:
            qc_out.qubits.remove(qubit)
    return qc_out


def get_qiskit_circuits(gate_sequences, gate_set, n_qubits, active_qubits):
    """
    Generate a set of Qiskit quantum circuits from specified gate sequences.

    This function creates a list of quantum circuits based on the provided sequences
    of gate indices. Each gate index corresponds to a gate in the provided `gate_set`.
    The gates are appended to a quantum circuit of a specified length and then measured.

    Parameters
    ----------
    gate_sequences : list of list of int
        A list where each element is a sequence of integers representing gate indices. Each integer
        corresponds to a gate in `gate_set`.
    gate_set : list
        A list of Qiskit gate objects. The indices in `gate_sequences` refer to gates in this list.
    n_qubits : int
        The total number of qubits in the system.
    active_qubits : list of int
        The qubits on which the circuits are run.


    Returns
    -------
    list of QuantumCircuit
        A list of Qiskit QuantumCircuit objects. Each circuit corresponds to one sequence in
        `gate_sequences`, with gates applied to the first qubit.
    """
    qiskit_circuits = []

    for gate_sequence in gate_sequences:
        qc = QuantumCircuit(n_qubits, n_qubits)
        for gate_num in gate_sequence:
            qc.compose(gate_set[gate_num], active_qubits, inplace=True)
            qc.barrier(active_qubits)
        qc.measure(active_qubits, active_qubits)
        qiskit_circuits.append(qc)
    return qiskit_circuits


def get_composed_qiskit_circuits(gate_sequences, gate_set, n_qubits, qubit_layouts, gate_context=None, parallel=False):
    """Turn GST sequences into Qiskit circuits, adding context gates if provided.

    For each GST sequence, either a single circuit is created for all qubit layouts if `parallel=True`, or a separate circuit if
    `parallel=False`.

    Parameters
    ----------
    gate_sequences : list of list of int
        Sequences of gate indices to apply. Each integer corresponds to a gate in the gate_set.
    gate_set : list
        The gate set defined as a list of Qiskit quantum circuits.
    n_qubits : int
        Total number of qubits in the system.
    qubit_layouts : list of list of int
        Lists of qubits on which the GST experiment is run.
    gate_context : QuantumCircuit or list of QuantumCircuit, optional
        Optional context circuit(s) to apply during each gate on qubits that are not measured for GST.
    parallel : bool, optional
        Whether GST for all qubits layouts is done in parallel on the backend.
        If True, applies gates to all qubit layouts in a single circuit.
        If False, creates separate circuits for each layout. Default is False.

    Returns
    -------
    list or list of list of QuantumCircuit
        If parallel=True: A list of QuantumCircuits, one for each gate sequence.
        If parallel=False: A list of lists of QuantumCircuits, where the outer list corresponds
        to qubit layouts and the inner list corresponds to gate sequences.
    """
    if gate_context is not None and not isinstance(gate_context, list):
        gate_context = [gate_context] * len(gate_set)
    qiskit_circuits = []
    if parallel:
        all_qubits = [q for qubits in qubit_layouts for q in qubits]
        all_clbits = [i for i, _ in enumerate(all_qubits)]
        for gate_sequence in gate_sequences:
            qc = QuantumCircuit(n_qubits, len(all_clbits))
            for gate_num in gate_sequence:
                if gate_context is not None:
                    qc.compose(gate_context[gate_num], inplace=True)
                for qubits in qubit_layouts:
                    qc.compose(gate_set[gate_num], qubits, inplace=True)
                qc.barrier()
            qc.measure(all_qubits, all_clbits)
            qiskit_circuits.append(qc)
    else:
        for qubits in qubit_layouts:
            clbits = [i for i, _ in enumerate(qubits)]
            layout_circuits = []
            for gate_sequence in gate_sequences:
                qc = QuantumCircuit(n_qubits, len(clbits))
                for gate_num in gate_sequence:
                    if gate_context is not None:
                        qc.compose(gate_context[gate_num], inplace=True)
                    qc.compose(gate_set[gate_num], qubits, inplace=True)
                    qc.barrier()
                qc.measure(qubits, clbits)
                layout_circuits.append(qc)
            qiskit_circuits.append(layout_circuits)
    return qiskit_circuits


def get_gate_sequence(sequence_number, sequence_length, gate_set_length):
    """Generate a set of random gate sequences.

    This function creates a specified number of random gate sequences, each of a given length.
    The gates are represented by numerical indices corresponding to elements in `gate_set`.
    Each sequence is a random combination of these indices.

    Parameters
    ----------
    sequence_number : int
        The number of gate sequences to generate.
    sequence_length : int
        The length of each gate sequence.
    gate_set_length : int
        The length of the set of gates to be used

    Returns
    -------
    numpy.ndarray
        An array of shape (sequence_number, sequence_length), where each row represents a
        randomly generated gate sequence.
    """
    J_rand = np.array(random.sample(range(gate_set_length**sequence_length), sequence_number))
    gate_sequences = np.array([low_level_jit.local_basis(ind, gate_set_length, sequence_length) for ind in J_rand])
    return gate_sequences


def job_counts_to_mgst_format(active_qubits, n_povm, result_dict):
    """Turns the dictionary of outcomes obtained from qiskit backend
        into the format which is used in mGST

    Parameters
    ----------
    active_qubits : list of int
        The qubits on which the circuits are run.
    n_povm : int
        Number of measurement outcomes, n_povm = physical dimension for basis measurements
    result_dict: (dict of str: int)
        Dictionary of outcomes from circuits run in a job
    Returns
    -------
    y : numpy array
        2D array of measurement outcomes for sequences in J;
        Each column contains the outcome probabilities for a fixed sequence

    """
    basis_dict_list = []
    for result in result_dict:
        # Translate dictionary entries of bitstring on the full system to the decimal representation of bitstrings on the active qubits
        basis_dict = {entry: int("".join([entry[::-1][i] for i in active_qubits][::-1]), 2) for entry in result}
        # Sort by index:
        basis_dict = dict(sorted(basis_dict.items(), key=lambda item: item[1]))
        basis_dict_list.append(basis_dict)
    y = []
    for i in range(len(result_dict)):
        row = [result_dict[i][key] for key in basis_dict_list[i]]
        if len(row) < n_povm:
            missing_entries = list(np.arange(n_povm))
            for given_entry in basis_dict_list[i].values():
                missing_entries.remove(given_entry)
            for missing_entry in missing_entries:
                row.insert(missing_entry, 0)  # 0 measurement outcomes in not recorded entry
        y.append(row / np.sum(row))
    y = np.array(y).T
    return y
