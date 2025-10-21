# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module containing Python wrapper for the qir-runner sparse quantum state simulator.

"""
import datetime
import logging
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import warnings
from collections import defaultdict
from typing import Any, Optional, Union

try:
    import numpy as np  # type: ignore
except ImportError:
    np = None  # type: ignore

from qbraid_core.annotations import deprecated
from qbraid_core.system.generic import _datetime_to_str, get_current_utc_datetime
from qbraid_core.system.versions import is_valid_semantic_version

from .exceptions import QuantumServiceRuntimeError

logger = logging.getLogger(__name__)


def measure_resource_usage():
    """Returns the current memory and CPU usage."""
    import psutil  # pylint: disable=import-outside-toplevel

    process = psutil.Process()
    memory_info = process.memory_info()
    cpu_percent = psutil.cpu_percent(interval=None)

    return memory_info.rss, cpu_percent  # rss: Resident Set Size (in bytes)


class QirRunner:
    """A sparse simulator that extends the functionality of the qir-runner.

    This simulator is a Python wrapper for the qir-runner, a command-line tool
    for executing compiled QIR files. It uses sparse matrices to represent quantum
    states and can be used to simulate quantum circuits that have been compiled to QIR.
    The simulator allows for setting a seed for random number generation and specifying
    an entry point for the execution.

    The qir-runner can be found at: https://github.com/qir-alliance/qir-runner

    Attributes:
        seed (optional, int): The value to use when seeding the random number generator used
                              for quantum simulation.
        exec_path (str): Path to the qir-runner executable.
        version (str): The version of the qir-runner executable.
    """

    def __init__(self, seed: Optional[int] = None, exec_path: Optional[str] = None):
        """Create a QIR runner simulator."""
        self.seed = seed
        self._version: Optional[str] = None
        self._qir_runner: Optional[str] = None

        try:
            self.set_path(exec_path)
        except (ValueError, FileNotFoundError) as err:
            warnings.warn(str(err), RuntimeWarning)

    @property
    def qir_runner(self) -> Optional[str]:
        """Path to the qir-runner executable."""
        return self._qir_runner

    @property
    def version(self) -> str:
        """Get the version of the qir-runner executable, caching the result."""
        if self._version is None and self._qir_runner:
            try:
                result = subprocess.run(
                    [self._qir_runner, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    raise QuantumServiceRuntimeError(result.stdout)

                version_info = result.stdout.strip()
                if version_info.startswith("qir-runner"):
                    runner_version = version_info.split()[-1]
                    if is_valid_semantic_version(runner_version):
                        self._version = runner_version
                    else:
                        warnings.warn(
                            f"Invalid qir-runner version '{runner_version}'. "
                            "Executable may be corrupt.",
                            RuntimeWarning,
                        )
            except Exception as err:  # pylint: disable=broad-exception-caught
                warnings.warn(f"Failed to determine qir-runner version: {err}", RuntimeWarning)

        return self._version or "Unknown"

    def set_path(self, value: Optional[str]) -> None:
        """Set the qir-runner path with additional validation."""
        resolved_path = shutil.which(value or "qir-runner")
        if resolved_path is None:
            if value is None:
                raise ValueError(
                    "No value was provided for the exec_path, "
                    "and the qir-runner executable was not found in the system PATH."
                )
            raise FileNotFoundError(
                f"The provided qir-runner executable path '{value}' does not exist."
            )

        self._qir_runner = resolved_path
        self._version = None  # Reset version cache since qir_runner changed

    def status(self) -> str:
        """Check the status of the qir-runner executable."""
        if self.qir_runner is None or self.version is None:
            return "UNAVAILABLE"

        return "ONLINE"

    @staticmethod  # pylint: disable-next=too-many-locals
    def _execute(command: list[str], **kwargs) -> dict[str, Any]:
        """Execute a subprocess command and return its output.

        Args:
            command (list[str]): The command to execute as a list of arguments.

        Returns:
            dict[str, Any]: A dictionary containing the status, stdout, stderr,
                            and timestamps related to the command execution.

        """
        status = "COMPLETED"
        result = {}

        memory_before, cpu_before = measure_resource_usage()
        created_at = get_current_utc_datetime()
        start = time.perf_counter()

        try:
            # Execute the command and capture both stdout and stderr
            process = subprocess.run(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                **kwargs,
            )
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            if process.returncode != 0:
                status = "FAILED"
        except subprocess.TimeoutExpired as err:
            status = "FAILED"
            result["stderr"] = f"Execution timed out after {err.timeout} seconds."
            logger.error("Timeout expired: %s. %s", command, err)
        except subprocess.CalledProcessError as err:
            status = "FAILED"
            result["stderr"] = f"Execution error. Exit code: {err.returncode}"
            logger.error(
                "Command failed with return code %s: %s. Stderr: %s",
                err.returncode,
                err.cmd,
                err.stderr,
            )
        finally:
            end = time.perf_counter()
            memory_after, cpu_after = measure_resource_usage()
            execution_duration = (end - start) * 1000  # Convert to milliseconds
            ended_at = created_at + datetime.timedelta(milliseconds=execution_duration)
            memory_mb = (memory_after - memory_before) / (1024**2)  # Convert bytes to MB
            cpu_percent = cpu_after - cpu_before  # CPU percentage

        result.update(
            {
                "status": status,
                "timeStamps": {
                    "createdAt": _datetime_to_str(created_at),
                    "endedAt": _datetime_to_str(ended_at),
                    "executionDuration": int(execution_duration),
                },
                "memoryUsageMb": max(0, memory_mb),
                "cpuUsagePercent": max(0, cpu_percent),
            }
        )

        return result

    @staticmethod
    def _parse_results(stdout: str) -> dict[str, list[int]]:
        """Parse the raw output from the execution to extract measurement results."""
        results = defaultdict(list)
        current_shot_results = []

        for line in stdout.splitlines():
            elements = line.split()
            if len(elements) == 3 and elements[:2] == ["OUTPUT", "RESULT"]:
                _, _, bit = elements
                current_shot_results.append(int(bit))
            elif line.startswith("END"):
                for idx, result in enumerate(current_shot_results):
                    results[f"q{idx}"].append(result)
                current_shot_results = []

        return dict(results)

    @staticmethod
    def _data_to_measurements(parsed_data: dict, numpy=np is not None) -> list:
        """Convert parsed data to a 2D array of measurement results."""
        data_lists = [parsed_data[key] for key in sorted(parsed_data.keys())]

        if numpy:
            data_array = np.array(data_lists, dtype=np.int8).T
            transposed_data = data_array.tolist()
        else:
            # Use the pure Python implementation if numpy is not installed
            transposed_data = list(map(list, zip(*data_lists)))

        return transposed_data

    @staticmethod
    def _measurements_to_counts(counts: list) -> dict[str, int]:
        """Convert measurements list to histogram data."""
        if not counts:
            return {}

        row_strings = ["".join(map(str, row)) for row in counts]
        hist_data = {row: row_strings.count(row) for row in set(row_strings)}
        counts_dict = {key.replace(" ", ""): value for key, value in hist_data.items()}
        num_bits = max(len(key) for key in counts_dict)
        all_keys = [format(i, f"0{num_bits}b") for i in range(2**num_bits)]
        final_counts = {key: counts_dict.get(key, 0) for key in sorted(all_keys)}
        non_zero_counts = {key: value for key, value in final_counts.items() if value != 0}
        return non_zero_counts

    def process_job_data(self, job_data: dict) -> dict:
        """
        Process the job data based on its status, parse the raw output,
        and update the job data with measurements and measurement counts.

        Args:
            job_data (dict): A dictionary containing details and results of a quantum job.

        Returns:
            dict: Updated job data with additional keys for measurements and counts, if applicable.
        """
        status = job_data.get("status")

        if status != "COMPLETED":
            return job_data

        try:
            raw_out = job_data.get("stdout", "")
            parsed_data = self._parse_results(raw_out)
            measurements = self._data_to_measurements(parsed_data)
            counts = self._measurements_to_counts(measurements)

            # Update job_data with the processed information
            job_data["measurements"] = measurements
            job_data["measurementCounts"] = counts
        except Exception as err:  # pylint: disable=broad-exception-caught
            logger.error("Error processing job data: %s", err)
            job_data["status"] = "FAILED"
            job_data["statusText"] = f"Uncaught {type(err).__name__} while processing job result."
        else:
            if not job_data.get("measurementCounts"):
                job_data["status"] = "FAILED"
                job_data["statusText"] = (
                    "Simulation returned no data. "
                    "Possible QIR bytecode incompatibility or no measurement gates."
                )

        return job_data

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def execute(
        self,
        qir_program: Optional[bytes] = None,
        file_path: Optional[Union[str, pathlib.Path]] = None,
        entrypoint: Optional[str] = None,
        shots: Optional[int] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Runs the qir-runner executable with the given QIR file and shots.

        Args:
            qir_program (optional, bytes): QIR module to run in the simulator.
            file_path (optional, Union[str, pathlib.Path]): Path to QIR file to run on simulator.
            entrypoint (optional, str): Name of the entrypoint function to execute in the QIR file.
            shots (optional, int): The number of times to repeat the execution of the chosen entry
                                point in the program. Defaults to 1.
            timeout (optional, float): Max number of seconds to wait for the command to complete.

        Returns:
            dict containing the job_id, measurement results, and execution duration.
        """
        if not qir_program and not file_path:
            raise ValueError("Either qir_program or file_path must be provided.")

        if qir_program and file_path:
            raise ValueError("Only one of qir_program or file_path should be provided.")

        if qir_program:
            tmp_dir = os.getenv("TMPDIR", "/tmp")
            local_store = pathlib.Path(tmp_dir)
            local_store.mkdir(
                parents=True, exist_ok=True
            )  # Create the directory if it doesn't exist

            # Use tempfile to automatically manage creation and deletion of the temp file
            with tempfile.NamedTemporaryFile(
                delete=False, dir=local_store, suffix=".bc"
            ) as temp_file:
                temp_file.write(qir_program)
                file_path = pathlib.Path(temp_file.name)  # Store file path to use in the command
        else:
            if not isinstance(file_path, (str, pathlib.Path)):
                raise ValueError("file_path must be a string or pathlib.Path object")

            file_path = pathlib.Path(file_path)

        if self.qir_runner is None:
            raise ValueError(
                "The qir-runner executable path has not been set. Use set_path() to set it."
            )

        try:
            # Construct the command
            command = [self.qir_runner, "--shots", str(shots or 1), "-f", str(file_path)]
            if entrypoint:
                command.extend(["-e", entrypoint])
            if self.seed is not None:
                command.extend(["-r", str(self.seed)])

            # Execute the qir-runner with the built command
            job_data = self._execute(command, timeout=timeout, **kwargs)
            job_data = self.process_job_data(job_data)
            job_data["runnerVersion"] = self.version
            job_data["runnerSeed"] = self.seed

            return job_data

        finally:
            # Ensure the temporary file is deleted even if an error occurs
            if qir_program:
                file_path.unlink(missing_ok=True)

    @deprecated("Use execute method instead.")
    def run(self, *args, **kwargs) -> dict[str, Any]:
        """Alias for execute method."""
        return self.execute(*args, **kwargs)

    def __eq__(self, other):
        """Check if two Simulator instances are equal based on their attributes."""
        if not isinstance(other, QirRunner):
            return NotImplemented
        return (
            (self.seed == other.seed)
            and (self.qir_runner == other.qir_runner)
            and (self.version == other.version)
        )

    def __repr__(self):
        return f"QirRunner(seed={self.seed}, exec_path={self.qir_runner}, version={self.version})"


class Simulator(QirRunner):
    """Deprecated class name for the QirRunner simulator."""
