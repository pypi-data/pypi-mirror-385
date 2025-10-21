"""
Mirror Randomized Benchmarking.
"""

from time import strftime, time
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Type
import warnings

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Clifford, random_clifford, random_pauli
from qiskit_aer import AerSimulator
from scipy.spatial.distance import hamming
import xarray as xr

from iqm.benchmarks import (
    BenchmarkAnalysisResult,
    BenchmarkObservation,
    BenchmarkObservationIdentifier,
    BenchmarkRunResult,
)
from iqm.benchmarks.benchmark import BenchmarkConfigurationBase
from iqm.benchmarks.benchmark_definition import Benchmark, add_counts_to_dataset
from iqm.benchmarks.circuit_containers import BenchmarkCircuit, CircuitGroup, Circuits
from iqm.benchmarks.logging_config import qcvv_logger
from iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common import (
    edge_grab,
    exponential_rb,
    fit_decay_lmfit,
    lmfit_minimizer,
    plot_rb_decay,
)
from iqm.benchmarks.utils import (
    get_iqm_backend,
    perform_backend_transpilation,
    retrieve_all_counts,
    retrieve_all_job_metadata,
    submit_execute,
    timeit,
    xrvariable_to_counts,
)
from iqm.qiskit_iqm import IQMCircuit as QuantumCircuit
from iqm.qiskit_iqm.iqm_backend import IQMBackendBase


def compute_polarizations(
    num_qubits: int,
    noisy_counts: List[Dict[str, int]],
    ideal_counts: List[Dict[str, int]],
    num_circ_samples: int,
    num_pauli_samples: int,
) -> List[float]:
    """Estimates the polarization for a list of noisy counts with respect to corresponding ideal counts
    The polarization here is a rescaling of the average fidelity, that corrects for few-qubit effects

    Arguments:
        num_qubits (int): the number of qubits being benchmarked
        noisy_counts (List[Dict[str, int]]): the list of counts coming from real execution
        ideal_counts (List[Dict[str, int]]): the list of counts coming from simulated, ideal execution
        num_circ_samples (int): the number circuit of samples used to estimate the polarization
        num_pauli_samples (int): the number of pauli samples per circuit sample used to estimate the polarization
    Returns:
        List[float]: the polarizations for each circuit sample of the given sequence length
    """
    ideal_counts_matrix = list_to_numcircuit_times_numpauli_matrix(ideal_counts, num_circ_samples, num_pauli_samples)
    noisy_counts_matrix = list_to_numcircuit_times_numpauli_matrix(noisy_counts, num_circ_samples, num_pauli_samples)

    polarizations: List = []
    for ideal_m, noisy_m in zip(ideal_counts_matrix, noisy_counts_matrix):
        polarization_pauli = []
        for ideal_pauli, noisy_pauli in zip(ideal_m, noisy_m):
            ideal_bitstrings = list(ideal_pauli.keys())
            noisy_bitstrings = list(noisy_pauli.keys())

            # Get the counts for each Hamming distance
            hamming_distances = {i: 0 for i in range(num_qubits + 1)}
            for s_n in noisy_bitstrings:
                for s_i in ideal_bitstrings:
                    k_index = int(hamming(list(s_n), list(s_i)) * num_qubits)
                    hamming_distances[k_index] += noisy_pauli[s_n]

            # Compute polarizations
            no_shots = sum(noisy_pauli.values())
            weighted_hamming = sum(((-1 / 2) ** k) * (hamming_distances[k] / no_shots) for k in range(num_qubits + 1))
            polarization_c = ((4**num_qubits) * weighted_hamming - 1) / (4**num_qubits - 1)
            polarization_pauli.append(polarization_c)

        # Average over the Pauli samples and add the circuit sample
        polarizations.append(np.mean(polarization_pauli))

    return polarizations


def generate_pauli_dressed_mrb_circuits(
    qubits: List[int],
    pauli_samples_per_circ: int,
    depth: int,
    backend_arg: IQMBackendBase | str,
    density_2q_gates: float = 0.25,
    two_qubit_gate_ensemble: Optional[Dict[str, float]] = None,
    clifford_sqg_probability=1.0,
    sqg_gate_ensemble: Optional[Dict[str, float]] = None,
    qiskit_optim_level: int = 1,
    routing_method: str = "basic",
    simulation_method: Literal[
        "automatic", "statevector", "stabilizer", "extended_stabilizer", "matrix_product_state"
    ] = "automatic",
) -> Dict[str, List[QuantumCircuit]]:
    """Samples a mirror circuit and generates samples of "Pauli-dressed" circuits,
        where for each circuit, random Pauli layers are interleaved between each layer of the circuit

    Args:
        qubits (List[int]): the qubits of the backend
        pauli_samples_per_circ (int): the number of pauli samples per circuit
        depth (int): the depth (number of canonical layers) of the circuit
        backend_arg (IQMBackendBase | str): the backend
        density_2q_gates (float): the expected density of 2Q gates
        two_qubit_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 2Q gates, and values being corresponding probabilities.
                * Default is None.
        clifford_sqg_probability (float): Probability with which to uniformly sample Clifford 1Q gates.
                * Default is 1.0.
        sqg_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities.
                * Default is None.
        qiskit_optim_level (int): Qiskit transpiler optimization level.
                * Default is 1.
        routing_method (str): Qiskit transpiler routing method.
                * Default is "basic".
        simulation_method (Literal["automatic", "statevector", "stabilizer", "extended_stabilizer", "matrix_product_state"]):
                Qiskit's Aer simulation method
                * Default is "automatic".
    Returns:
        Dict[str, List[QuantumCircuit]]
    """
    num_qubits = len(qubits)

    # Sample the layers using edge grab sampler - different samplers may be conditionally chosen here in the future
    cycle_layers = edge_grab(
        qubits,
        depth,
        backend_arg,
        density_2q_gates,
        two_qubit_gate_ensemble,
        clifford_sqg_probability,
        sqg_gate_ensemble,
    )

    # Sample the edge (initial/final) random Single-qubit Clifford layer
    clifford_layer = [random_clifford(1) for _ in range(num_qubits)]

    # Initialize the list of circuits
    all_circuits = {}
    pauli_dressed_circuits_untranspiled: List[QuantumCircuit] = []
    pauli_dressed_circuits_transpiled: List[QuantumCircuit] = []

    simulator = AerSimulator(method=simulation_method)

    for _ in range(pauli_samples_per_circ):
        # Initialize the quantum circuit object
        circ = QuantumCircuit(num_qubits)
        # Sample all the random Paulis
        paulis = [random_pauli(num_qubits) for _ in range(depth + 1)]

        # Add the edge product of Cliffords
        for i in range(num_qubits):
            circ.compose(clifford_layer[i].to_instruction(), qubits=[i], inplace=True)
        circ.barrier()

        # Add the cycle layers
        for k in range(depth):
            circ.compose(
                paulis[k].to_instruction(),
                qubits=list(range(num_qubits)),
                inplace=True,
            )
            circ.barrier()
            circ.compose(cycle_layers[k], inplace=True)
            circ.barrier()

        # Apply middle Pauli
        circ.compose(
            paulis[depth].to_instruction(),
            qubits=list(range(num_qubits)),
            inplace=True,
        )
        circ.barrier()

        # Add the mirror layers
        for k in range(depth):
            circ.compose(cycle_layers[depth - k - 1].inverse(), inplace=True)
            circ.barrier()
            circ.compose(
                paulis[depth - k - 1].to_instruction(),
                qubits=list(range(num_qubits)),
                inplace=True,
            )
            circ.barrier()

        # Add the inverse edge product of Cliffords
        for i in range(num_qubits):
            circ.compose(clifford_layer[i].to_instruction().inverse(), qubits=[i], inplace=True)

        # Transpile to backend - no optimize SQG should be used!
        if isinstance(backend_arg, str):
            retrieved_backend = get_iqm_backend(backend_arg)
        else:
            assert isinstance(backend_arg, IQMBackendBase)
            retrieved_backend = backend_arg

        circ_untransp = circ.copy()
        # Add measurements to untranspiled - after!
        circ_untranspiled = transpile(Clifford(circ_untransp).to_circuit(), simulator)
        circ_untranspiled.measure_all()

        # Add measurements to transpiled - before!
        circ.measure_all()
        if "move" in retrieved_backend.architecture.gates:
            # All-to-all coupling map on the active qubits
            effective_coupling_map = [[x, y] for x in qubits for y in qubits if x != y]
        else:
            effective_coupling_map = retrieved_backend.coupling_map
        circ_transpiled, _ = perform_backend_transpilation(
            [circ],
            backend=retrieved_backend,
            qubits=qubits,
            coupling_map=effective_coupling_map,
            qiskit_optim_level=qiskit_optim_level,
            routing_method=routing_method,
        )

        pauli_dressed_circuits_untranspiled.append(circ_untranspiled)
        pauli_dressed_circuits_transpiled.append(circ_transpiled[0])

    # Store the circuit
    all_circuits.update(
        {
            "untranspiled": pauli_dressed_circuits_untranspiled,
            "transpiled": pauli_dressed_circuits_transpiled,
        }
    )

    return all_circuits


@timeit
def generate_fixed_depth_mrb_circuits(
    qubits: List[int],
    circ_samples: int,
    pauli_samples_per_circ: int,
    depth: int,
    backend_arg: IQMBackendBase | str,
    density_2q_gates: float = 0.25,
    two_qubit_gate_ensemble: Optional[Dict[str, float]] = None,
    clifford_sqg_probability=1.0,
    sqg_gate_ensemble: Optional[Dict[str, float]] = None,
    qiskit_optim_level: int = 1,
    routing_method: str = "basic",
    simulation_method: Literal[
        "automatic", "statevector", "stabilizer", "extended_stabilizer", "matrix_product_state"
    ] = "automatic",
) -> Dict[int, Dict[str, List[QuantumCircuit]]]:
    """Generates a dictionary MRB circuits at fixed depth, indexed by sample number

    Args:
        qubits (List[int]): A list of integers specifying physical qubit labels
        circ_samples (int): The number of sets of Pauli-dressed circuit samples
        pauli_samples_per_circ (int): the number of pauli samples per circuit
        depth (int): the depth (number of canonical layers) of the circuits
        backend_arg (IQMBackendBase | str): the backend
        density_2q_gates (float): the expected density of 2Q gates
        two_qubit_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 2Q gates, and values being corresponding probabilities.
                * Default is None.
        two_qubit_gate_ensemble (Optional[Dict[str, float]]):
        clifford_sqg_probability (float): Probability with which to uniformly sample Clifford 1Q gates.
                * Default is 1.0.
        sqg_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities.
                * Default is None.
        qiskit_optim_level (int): Qiskit transpiler optimization level.
                * Default is 1.
        routing_method (str): Qiskit transpiler routing method.
                * Default is "basic".
        simulation_method (Literal["automatic", "statevector", "stabilizer", "extended_stabilizer", "matrix_product_state"]):
                            Qiskit's Aer simulation method
                            * Default is "automatic".
    Returns:
        A dictionary of lists of Pauli-dressed quantum circuits corresponding to the circuit sample index
    """

    circuits = {}  # The dict with a Dict of random mirror circuits
    for p_sample in range(circ_samples):
        circuits[p_sample] = generate_pauli_dressed_mrb_circuits(
            qubits,
            pauli_samples_per_circ,
            depth,
            backend_arg,
            density_2q_gates,
            two_qubit_gate_ensemble,
            clifford_sqg_probability,
            sqg_gate_ensemble,
            qiskit_optim_level=qiskit_optim_level,
            routing_method=routing_method,
            simulation_method=simulation_method,
        )

    return circuits


def list_to_numcircuit_times_numpauli_matrix(
    input_list: List[Any], num_circ_samples: int, num_pauli_samples: int
) -> List[List[Any]]:
    """Convert a flat list to a matrix of shape (num_circ_samples, num_pauli_samples).
    Args:
        input_list (List[Any]): the input flat list
        num_circ_samples (int): the number of sets of Pauli-dressed circuit samples
        num_pauli_samples (int): the number of Pauli samples per circuit
    Raises:
        ValueError: Length of passed list is not (num_circ_samples * num_pauli_samples).
    Returns:
        List[List[Any]]: the matrix
    """
    if len(input_list) != num_circ_samples * num_pauli_samples:
        raise ValueError(
            f"Length of passed list {len(input_list)} is not"
            f" (num_circ_samples * num_pauli_samples) = {num_circ_samples * num_pauli_samples}"
        )

    return np.reshape(input_list, (num_circ_samples, num_pauli_samples)).tolist()


# pylint: disable=too-many-statements
def mrb_analysis(run: BenchmarkRunResult) -> BenchmarkAnalysisResult:
    """Analysis function for a MRB experiment

    Args:
        run (RunResult): A MRB experiment run for which analysis result is created
    Returns:
        AnalysisResult corresponding to MRB
    """
    plots = {}
    obs_dict = {}
    observations: list[BenchmarkObservation] = []
    dataset = run.dataset.copy(deep=True)

    # shots = dataset.attrs["shots"]
    num_circuit_samples = dataset.attrs["num_circuit_samples"]
    num_pauli_samples = dataset.attrs["num_pauli_samples"]

    density_2q_gates = dataset.attrs["density_2q_gates"]
    two_qubit_gate_ensemble = dataset.attrs["two_qubit_gate_ensemble"]

    # max_gates_per_batch = dataset.attrs["max_gates_per_batch"]

    # Analyze the results for each qubit layout of the experiment dataset
    qubits_array = dataset.attrs["qubits_array"]
    depths_array = dataset.attrs["depths_array"]

    assigned_mrb_depths = {}
    if len(qubits_array) != len(depths_array):
        # If user did not specify a list of depth for each list of qubits, assign the first
        # If the len is not one, the input was incorrect
        if len(depths_array) != 1:
            qcvv_logger.info(
                f"The amount of qubit layouts ({len(qubits_array)}) is not the same "
                f"as the amount of depth configurations ({len(depths_array)}):\n\tWill assign to all the first "
                f"configuration: {depths_array[0]} !"
            )
        assigned_mrb_depths = {str(q): [2 * m for m in depths_array[0]] for q in qubits_array}
    else:
        assigned_mrb_depths = {str(qubits_array[i]): [2 * m for m in depths_array[i]] for i in range(len(depths_array))}

    mrb_sim_circuits = run.circuits["untranspiled_circuits"]
    sim_method = "stabilizer"
    simulator = AerSimulator(method=sim_method)  # Aer.get_backend("stabilizer")

    all_noisy_counts: Dict[str, Dict[int, List[Dict[str, int]]]] = {}
    all_noiseless_counts: Dict[str, Dict[int, List[Dict[str, int]]]] = {}
    time_retrieve_noiseless: Dict[str, Dict[int, float]] = {}
    # Need to loop over each set of qubits, and within, over each depth
    for qubits_idx, qubits in enumerate(qubits_array):
        polarizations = {}
        num_qubits = len(qubits)
        all_noisy_counts[str(qubits)] = {}
        all_noiseless_counts[str(qubits)] = {}
        time_retrieve_noiseless[str(qubits)] = {}
        qcvv_logger.info(f"Post-processing MRB for qubits {qubits}")
        for depth in assigned_mrb_depths[str(qubits)]:
            # Retrieve counts
            identifier = f"qubits_{str(qubits)}_depth_{str(depth)}"
            all_noisy_counts[str(qubits)][depth] = xrvariable_to_counts(
                dataset, identifier, num_circuit_samples * num_pauli_samples
            )
            qcvv_logger.info(f"Depth {depth}")

            mrb_circs = mrb_sim_circuits[f"{str(qubits)}_depth_{str(depth)}"].circuits

            qcvv_logger.info("Getting simulation counts")
            all_noiseless_counts[str(qubits)][depth] = simulator.run(mrb_circs).result().get_counts()

            # Compute polarizations for the current depth
            polarizations[depth] = compute_polarizations(
                num_qubits,
                all_noisy_counts[str(qubits)][depth],
                all_noiseless_counts[str(qubits)][depth],
                num_circuit_samples,
                num_pauli_samples,
            )

        # Fit decay and extract parameters
        list_of_polarizations = list(polarizations.values())
        fit_data, fit_parameters = fit_decay_lmfit(exponential_rb, qubits, list_of_polarizations, "mrb")
        rb_fit_results = lmfit_minimizer(fit_parameters, fit_data, assigned_mrb_depths[str(qubits)], exponential_rb)

        average_polarizations = {d: np.mean(polarizations[d]) for d in assigned_mrb_depths[str(qubits)]}
        stddevs_from_mean = {
            d: np.std(polarizations[d]) / np.sqrt(num_circuit_samples * num_pauli_samples)
            for d in assigned_mrb_depths[str(qubits)]
        }
        popt = {
            "amplitude": rb_fit_results.params["amplitude_1"],
            "offset": rb_fit_results.params["offset_1"],
            "decay_rate": rb_fit_results.params["p_mrb"],
        }
        fidelity = rb_fit_results.params["fidelity_mrb"]

        processed_results = {
            "average_gate_fidelity": {"value": fidelity.value, "uncertainty": fidelity.stderr},
        }

        dataset.attrs[qubits_idx].update(
            {
                "decay_rate": {"value": popt["decay_rate"].value, "uncertainty": popt["decay_rate"].stderr},
                "fit_amplitude": {"value": popt["amplitude"].value, "uncertainty": popt["amplitude"].stderr},
                "fit_offset": {"value": popt["offset"].value, "uncertainty": popt["offset"].stderr},
                "polarizations": polarizations,
                "average_polarization_nominal_values": average_polarizations,
                "average_polarization_stderr": stddevs_from_mean,
                "fitting_method": str(rb_fit_results.method),
                "num_function_evals": int(rb_fit_results.nfev),
                "data_points": int(rb_fit_results.ndata),
                "num_variables": int(rb_fit_results.nvarys),
                "chi_square": float(rb_fit_results.chisqr),
                "reduced_chi_square": float(rb_fit_results.redchi),
                "Akaike_info_crit": float(rb_fit_results.aic),
                "Bayesian_info_crit": float(rb_fit_results.bic),
            }
        )

        # Update observations
        obs_dict.update({qubits_idx: processed_results})

        # Generate plots
        fig_name, fig = plot_rb_decay(
            "mrb",
            [qubits],
            dataset,
            obs_dict,
            mrb_2q_density=density_2q_gates,
            mrb_2q_ensemble=two_qubit_gate_ensemble,
        )
        plots[fig_name] = fig

        observations.extend(
            [
                BenchmarkObservation(
                    name="decay_rate",
                    identifier=BenchmarkObservationIdentifier(qubits),
                    value=popt["decay_rate"].value,
                    uncertainty=popt["decay_rate"].stderr,
                )
            ]
        )

    # Generate the combined plot
    fig_name, fig = plot_rb_decay(
        "mrb",
        qubits_array,
        dataset,
        obs_dict,
        mrb_2q_density=density_2q_gates,
        mrb_2q_ensemble=two_qubit_gate_ensemble,
    )
    plots[fig_name] = fig

    return BenchmarkAnalysisResult(dataset=dataset, plots=plots, observations=observations)


class MirrorRandomizedBenchmarking(Benchmark):
    """
    Mirror RB estimates the fidelity of ensembles of n-qubit layers
    """

    analysis_function = staticmethod(mrb_analysis)

    name: str = "mirror_rb"

    def __init__(self, backend_arg: IQMBackendBase | str, configuration: "MirrorRBConfiguration"):
        """Construct the MirrorRandomizedBenchmarking class

        Args:
            backend_arg (IQMBackendBase | str): _description_
            configuration (MirrorRBConfiguration): _description_
        """
        super().__init__(backend_arg, configuration)

        # EXPERIMENT
        self.backend_configuration_name = backend_arg if isinstance(backend_arg, str) else backend_arg.name

        self.qubits_array = configuration.qubits_array
        self.depths_array = configuration.depths_array

        self.num_circuit_samples = configuration.num_circuit_samples
        self.num_pauli_samples = configuration.num_pauli_samples

        self.two_qubit_gate_ensemble = configuration.two_qubit_gate_ensemble
        self.density_2q_gates = configuration.density_2q_gates
        self.clifford_sqg_probability = configuration.clifford_sqg_probability
        self.sqg_gate_ensemble = configuration.sqg_gate_ensemble

        self.qiskit_optim_level = configuration.qiskit_optim_level

        self.simulation_method = configuration.simulation_method

        self.session_timestamp = strftime("%Y%m%d-%H%M%S")
        self.execution_timestamp = ""

        # Initialize the variable to contain the circuits for each layout
        self.untranspiled_circuits = BenchmarkCircuit("untranspiled_circuits")
        self.transpiled_circuits = BenchmarkCircuit("transpiled_circuits")

    def add_all_meta_to_dataset(self, dataset: xr.Dataset):
        """Adds all configuration metadata and circuits to the dataset variable

        Args:
            dataset (xr.Dataset): The xarray dataset
        """
        dataset.attrs["session_timestamp"] = self.session_timestamp
        dataset.attrs["execution_timestamp"] = self.execution_timestamp
        dataset.attrs["backend_configuration_name"] = self.backend_configuration_name
        dataset.attrs["backend_name"] = self.backend.name

        for key, value in self.configuration:
            if key == "benchmark":  # Avoid saving the class object
                dataset.attrs[key] = value.name
            else:
                dataset.attrs[key] = value
        # Defined outside configuration - if any

    def submit_single_mrb_job(
        self,
        backend_arg: IQMBackendBase,
        qubits: Sequence[int],
        depth: int,
        sorted_transpiled_circuit_dicts: Dict[Tuple[int, ...], List[QuantumCircuit]],
    ) -> Dict[str, Any]:
        """
        Submit fixed-depth MRB jobs for execution in the specified IQMBackend

        Args:
            backend_arg (IQMBackendBase): the IQM backend to submit the job
            qubits (Sequence[int]): the qubits to identify the submitted job
            depth (int): the depth (number of canonical layers) of the circuits to identify the submitted job
            sorted_transpiled_circuit_dicts (Dict[str, List[QuantumCircuit]]): A dictionary containing all MRB circuits
        Returns:
            Dict with qubit layout, submitted job objects, type (vanilla/DD) and submission time
        """
        # Submit
        # Send to execute on backend
        execution_jobs, time_submit = submit_execute(
            sorted_transpiled_circuit_dicts,
            backend_arg,
            self.shots,
            self.calset_id,
            max_gates_per_batch=self.max_gates_per_batch,
            max_circuits_per_batch=self.configuration.max_circuits_per_batch,
            circuit_compilation_options=self.circuit_compilation_options,
        )
        mrb_submit_results = {
            "qubits": qubits,
            "depth": depth,
            "jobs": execution_jobs,
            "time_submit": time_submit,
        }
        return mrb_submit_results

    def execute(self, backend: IQMBackendBase) -> xr.Dataset:
        """Executes the benchmark"""

        self.execution_timestamp = strftime("%Y%m%d-%H%M%S")

        dataset = xr.Dataset()
        self.add_all_meta_to_dataset(dataset)

        # Submit jobs for all qubit layouts
        all_mrb_jobs: List[Dict[str, Any]] = []
        time_circuit_generation: Dict[str, float] = {}
        total_submit: float = 0
        total_retrieve: float = 0

        # The depths should be assigned to each set of qubits!
        # The real final MRB depths are twice the originally specified, must be taken into account here!
        assigned_mrb_depths = {}
        if len(self.qubits_array) != len(self.depths_array):
            # If user did not specify a list of depth for each list of qubits, assign the first
            # If the len is not one, the input was incorrect
            if len(self.depths_array) != 1:
                warnings.warn(
                    f"The amount of qubit layouts ({len(self.qubits_array)}) is not the same "
                    f"as the amount of depth configurations ({len(self.depths_array)}):\n\tWill assign to all the first "
                    f"configuration: {self.depths_array[0]} !"
                )
            assigned_mrb_depths = {str(q): [2 * m for m in self.depths_array[0]] for q in self.qubits_array}
        else:
            assigned_mrb_depths = {
                str(self.qubits_array[i]): [2 * m for m in self.depths_array[i]] for i in range(len(self.depths_array))
            }

        # Auxiliary dict from str(qubits) to indices
        qubit_idx: Dict[str, Any] = {}
        for qubits_idx, qubits in enumerate(self.qubits_array):
            qubit_idx[str(qubits)] = qubits_idx

            qcvv_logger.info(
                f"Executing MRB on qubits {qubits}."
                f" Will generate and submit all {self.num_circuit_samples}x{self.num_pauli_samples} MRB circuits"
                f" for each depth {assigned_mrb_depths[str(qubits)]}"
            )
            mrb_circuits = {}
            mrb_transpiled_circuits_lists: Dict[int, List[QuantumCircuit]] = {}
            mrb_untranspiled_circuits_lists: Dict[int, List[QuantumCircuit]] = {}
            time_circuit_generation[str(qubits)] = 0
            for depth in assigned_mrb_depths[str(qubits)]:
                qcvv_logger.info(f"Depth {depth} - Generating all circuits")
                mrb_circuits[depth], elapsed_time = generate_fixed_depth_mrb_circuits(
                    qubits,
                    self.num_circuit_samples,
                    self.num_pauli_samples,
                    int(depth / 2),
                    backend,
                    self.density_2q_gates,
                    self.two_qubit_gate_ensemble,
                    self.clifford_sqg_probability,
                    self.sqg_gate_ensemble,
                    self.qiskit_optim_level,
                    self.routing_method,
                    self.simulation_method,
                )
                time_circuit_generation[str(qubits)] += elapsed_time

                # Generated circuits at fixed depth are (dict) indexed by Pauli sample number, turn into List
                mrb_transpiled_circuits_lists[depth] = []
                mrb_untranspiled_circuits_lists[depth] = []
                for c_s in range(self.num_circuit_samples):
                    mrb_transpiled_circuits_lists[depth].extend(mrb_circuits[depth][c_s]["transpiled"])
                for c_s in range(self.num_circuit_samples):
                    mrb_untranspiled_circuits_lists[depth].extend(mrb_circuits[depth][c_s]["untranspiled"])

                # Submit
                sorted_transpiled_qc_list = {tuple(qubits): mrb_transpiled_circuits_lists[depth]}
                t_start = time()
                all_mrb_jobs.append(self.submit_single_mrb_job(backend, qubits, depth, sorted_transpiled_qc_list))
                total_retrieve += time() - t_start
                qcvv_logger.info(f"Job for layout {qubits} & depth {depth} submitted successfully!")

                self.untranspiled_circuits.circuit_groups.append(
                    CircuitGroup(name=f"{str(qubits)}_depth_{depth}", circuits=mrb_untranspiled_circuits_lists[depth])
                )
                self.transpiled_circuits.circuit_groups.append(
                    CircuitGroup(name=f"{str(qubits)}_depth_{depth}", circuits=mrb_transpiled_circuits_lists[depth])
                )

            dataset.attrs[qubits_idx] = {"qubits": qubits}

        # Retrieve counts of jobs for all qubit layouts
        for job_dict in all_mrb_jobs:
            qubits = job_dict["qubits"]
            depth = job_dict["depth"]
            # Retrieve counts
            execution_results, time_retrieve = retrieve_all_counts(
                job_dict["jobs"], f"qubits_{str(qubits)}_depth_{str(depth)}"
            )
            # Retrieve all job meta data
            all_job_metadata = retrieve_all_job_metadata(job_dict["jobs"])
            total_retrieve += time_retrieve
            # Export all to dataset
            dataset.attrs[qubit_idx[str(qubits)]].update(
                {
                    f"depth_{str(depth)}": {
                        "time_circuit_generation": time_circuit_generation[str(qubits)],
                        "time_submit": job_dict["time_submit"],
                        "time_retrieve": time_retrieve,
                        "all_job_metadata": all_job_metadata,
                    },
                }
            )

            qcvv_logger.info(f"Adding counts of qubits {qubits} and depth {depth} run to the dataset")
            dataset, _ = add_counts_to_dataset(execution_results, f"qubits_{str(qubits)}_depth_{str(depth)}", dataset)

        dataset.attrs["total_submit_time"] = total_submit
        dataset.attrs["total_retrieve_time"] = total_retrieve
        self.circuits = Circuits([self.transpiled_circuits, self.untranspiled_circuits])

        qcvv_logger.info(f"MRB experiment execution concluded !")

        return dataset


class MirrorRBConfiguration(BenchmarkConfigurationBase):
    """Mirror RB configuration.

    Attributes:
        benchmark (Type[Benchmark]): MirrorRandomizedBenchmarking.
        qubits_array (Sequence[Sequence[int]]): The array of physical qubits in which to execute MRB.
        depths_array (Sequence[Sequence[int]]): The array of physical depths in which to execute MRB for a corresponding qubit list.
                            * If len is the same as that of qubits_array, each Sequence[int] corresponds to the depths for the corresponding layout of qubits.
                            * If len is different from that of qubits_array, assigns the first Sequence[int].
        num_circuit_samples (int): The number of random-layer mirror circuits to generate.
        num_pauli_samples (int): The number of random Pauli layers to interleave per mirror circuit.
        shots (int): The number of measurement shots to execute per circuit.
        qiskit_optim_level (int): The Qiskit-level of optimization to use in transpilation.
                            * Default is 1.
        routing_method (Literal["basic", "lookahead", "stochastic", "sabre", "none"]): The routing method to use in transpilation.
                            * Default is "sabre".
        two_qubit_gate_ensemble (Dict[str, float]): The two-qubit gate ensemble to use in the random mirror circuits.
                            * Keys correspond to str names of qiskit circuit library gates, e.g., "CZGate" or "CXGate".
                            * Values correspond to the probability for the respective gate to be sampled.
                            * Default is {"CZGate": 1.0}.
        density_2q_gates (float): The expected density of 2-qubit gates in the final circuits.
                            * Default is 0.25.
        clifford_sqg_probability (float): Probability with which to uniformly sample Clifford 1Q gates.
                * Default is 1.0.
        sqg_gate_ensemble (Optional[Dict[str, float]]): A dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities.
                * Default is None.
        simulation_method (Literal["automatic", "statevector", "stabilizer", "extended_stabilizer", "matrix_product_state"]):
                            Qiskit's Aer simulation method
                            * Default is "automatic".
    """

    benchmark: Type[Benchmark] = MirrorRandomizedBenchmarking
    qubits_array: Sequence[Sequence[int]]
    depths_array: Sequence[Sequence[int]]
    num_circuit_samples: int
    num_pauli_samples: int
    qiskit_optim_level: int = 1
    two_qubit_gate_ensemble: Dict[str, float] = {
        "CZGate": 1.0,
    }
    density_2q_gates: float = 0.25
    clifford_sqg_probability: float = 1.0
    sqg_gate_ensemble: Optional[Dict[str, float]] = None
    simulation_method: Literal[
        "automatic", "statevector", "stabilizer", "extended_stabilizer", "matrix_product_state"
    ] = "automatic"
