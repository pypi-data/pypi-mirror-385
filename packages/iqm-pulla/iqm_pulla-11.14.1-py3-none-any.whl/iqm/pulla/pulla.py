# Copyright 2024-2025 IQM
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

"""Pulse level access library for IQM's circuit-to-pulse compiler and Station Control API."""

from collections.abc import Callable
from importlib.metadata import version
import logging
import platform
import time
from typing import Any
import uuid

import requests

from exa.common.data.setting_node import SettingNode
from exa.common.logger import init_loggers
from exa.common.qcm_data.chip_topology import ChipTopology
from iqm.cpc.compiler.compiler import (
    STANDARD_CIRCUIT_EXECUTION_OPTIONS,
    STANDARD_CIRCUIT_EXECUTION_OPTIONS_DICT,
    Compiler,
)
from iqm.cpc.compiler.standard_stages import get_standard_stages
from iqm.cpc.interface.compiler import CircuitExecutionOptions
from iqm.pulla.calibration import CalibrationDataProvider
from iqm.pulla.interface import (
    CalibrationSet,
    CalibrationSetId,
    CHADRetrievalException,
    ChipLabelRetrievalException,
    SettingsRetrievalException,
    StationControlResult,
    TaskStatus,
)
from iqm.pulla.utils import extract_readout_controller_result_names, map_sweep_results_to_logical_qubits
from iqm.pulse.playlist.channel import ChannelProperties, get_channel_properties_from_station_settings
from iqm.pulse.playlist.playlist import Playlist
from iqm.station_control.client.utils import get_progress_bar_callback, init_station_control
from iqm.station_control.interface.models import JobExecutorStatus, SweepDefinition

#    ██████  ██    ██ ██      ██       █████
#    ██   ██ ██    ██ ██      ██      ██   ██
#    ██████  ██    ██ ██      ██      ███████
#    ██      ██    ██ ██      ██      ██   ██
#    ██       ██████  ███████ ███████ ██   ██

logger = logging.getLogger(__name__)


class Pulla:
    """Pulse level access library for IQM's circuit-to-pulse compiler and Station Control API.
    Conceptually, represents a connection to a remote quantum computer, and a provider of calibration data.
    Can create a compiler instance ready to be used with the connected quantum computer.

    Args:
        station_control_url: URL to a Station Control instance.
        get_token_callback: An optional function that returns an authentication token for the Station Control API.

    """

    def __init__(
        self,
        station_control_url: str,
        *,
        get_token_callback: Callable[[], str] | None = None,
        **kwargs,
    ):
        self._signature = f"{platform.platform(terse=True)}"
        self._signature += f", python {platform.python_version()}"
        self._signature += f", iqm-pulla {version('iqm-pulla')}"

        # The function to be passed to Station Control Client if the server requires authentication
        self.get_token_callback = get_token_callback

        # SC Client to be used for fetching calibration data, submitting sweeps, and retrieving results.
        try:
            self._station_control = init_station_control(
                station_control_url, get_token_callback=self.get_token_callback, **kwargs
            )

        except Exception as e:
            logger.error("Failed to initialize Station Control Client: %s", e)
            raise ValueError("Failed to initialize Station Control Client") from e
        # Separate wrapper on top of SC Client to simplify calibration data fetching.
        self._calibration_data_provider = CalibrationDataProvider(self._station_control)

        # Data needed for the compiler.
        self._station_control_settings: SettingNode | None = None
        self._chip_topology: ChipTopology = self.get_chip_topology()
        self._chip_label: str = self.get_chip_label()

        self._channel_properties: dict[str, ChannelProperties]
        self._component_channels: dict[str, dict[str, str]]
        self._channel_properties, self._component_channels = self.get_channel_properties()

    def get_standard_compiler(
        self,
        calibration_set: CalibrationSet | None = None,
        circuit_execution_options: CircuitExecutionOptions | dict | None = None,
    ) -> Compiler:
        """Returns a new instance of the compiler with the default calibration set and standard stages.

        Args:
            calibration_set: Calibration set to use. If None, the default calibration set will be used.
            circuit_execution_options: circuit execution options to use for the compiler. If a CircuitExecutionOptions
                object is provided, the compiler use it as is. If a dict is provided, the default values will be
                overridden for the present keys in that dict. If left ``None``, the default options will be used.

        Returns:
            The compiler object.

        """
        if circuit_execution_options is None:
            circuit_execution_options = STANDARD_CIRCUIT_EXECUTION_OPTIONS
        elif isinstance(circuit_execution_options, dict):
            circuit_execution_options = CircuitExecutionOptions(
                **STANDARD_CIRCUIT_EXECUTION_OPTIONS_DICT | circuit_execution_options  # type: ignore
            )
        return Compiler(
            calibration_set=calibration_set or self.fetch_latest_calibration_set()[0],
            chip_topology=self._chip_topology,
            channel_properties=self._channel_properties,
            component_channels=self._component_channels,
            component_mapping=None,
            stages=get_standard_stages(),
            options=circuit_execution_options,
        )

    def fetch_latest_calibration_set(self) -> tuple[CalibrationSet, CalibrationSetId]:
        """Fetches the latest default calibration set from the server, and returns its decoded representation and id."""  # noqa: E501
        latest_calibration_set, latest_calibration_set_id = self._calibration_data_provider.get_latest_calibration_set(
            self.get_chip_label()
        )
        return latest_calibration_set, latest_calibration_set_id

    def fetch_calibration_set_by_id(self, calibration_set_id: CalibrationSetId) -> CalibrationSet:
        """Fetches a specific calibration set from the server, and returns its decoded representation.
        All calibration sets are cached in-memory, so if the calibration set with the given id has already been fetched,
        it will be returned immediately.

        Args:
            calibration_set_id: id of the calibration set to fetch.

        """
        calibration_set = self._calibration_data_provider.get_calibration_set(calibration_set_id)
        return calibration_set

    def get_chip_label(self) -> str:
        """Returns the chip label of the current quantum computer.

        The chip label is fetched from the Station Control API.
        """
        try:
            duts = self._station_control.get_duts()
        except requests.RequestException as e:
            raise ChipLabelRetrievalException(f"Failed to retrieve the chip label: {e}") from e

        if len(duts) != 1:
            raise ChipLabelRetrievalException(f"Expected exactly one chip label, but got {len(duts)}")
        return duts[0].label

    def get_chip_topology(self) -> ChipTopology:
        """Returns chip topology that was fetched from the IQM server during Pulla initialization."""
        try:
            record = self._station_control.get_chip_design_record(self.get_chip_label())
        except Exception as e:
            raise CHADRetrievalException("Could not fetch chip design record") from e
        return ChipTopology.from_chip_design_record(record)

    def _get_station_control_settings(self) -> SettingNode:
        """Returns the Station Control settings node that was fetched from the IQM server during Pulla initialization."""  # noqa: E501
        if self._station_control_settings is None:
            # request the station settings, cache the results
            try:
                self._station_control_settings = self._station_control.get_settings()
            except Exception as e:
                raise SettingsRetrievalException("Could not fetch station settings") from e
        return self._station_control_settings

    def get_channel_properties(
        self,
    ) -> tuple[dict[str, ChannelProperties], dict[str, dict[str, str]]]:
        """Control channel properties from Station Control controller settings.

        Returns:
            channel_properties: Mapping from channel names to  their properties.
            component_to_channel: Mapping from chip component names to functions to channel names.
                For example, `'QB1' -> 'drive' -> 'QB1__drive.awg'`

        """
        return get_channel_properties_from_station_settings(
            self._get_station_control_settings(), self.get_chip_topology()
        )

    def execute(
        self,
        playlist: Playlist,
        context: dict[str, Any],
        settings: SettingNode,
        verbose: bool = True,
        wait_completion: bool = True,
    ) -> StationControlResult:
        """Executes a quantum circuit on the remote quantum computer.

        Args:
            playlist: Final schedule to be executed.
            context: Context object of the successful compiler run, containing the readout mappings.
            settings: Station settings.
            verbose: Whether to print results.
            wait_completion: If True, returns immediately with job ID. If False, waits for completion.

        Returns:
            results of the execution

        """
        readout_components = []
        for _, channel in self._component_channels.items():
            for k, v in channel.items():
                if k == "readout":
                    readout_components.append(v)

        sweep_response = self._station_control.sweep(
            SweepDefinition(
                sweep_id=uuid.uuid4(),
                playlist=playlist,
                return_parameters=list(extract_readout_controller_result_names(context["readout_mappings"])),
                settings=settings,
                dut_label=self.get_chip_label(),
                sweeps=[],
            )
        )
        job_id = uuid.UUID(sweep_response["job_id"])

        logger.info("Created job in queue with ID: %s", job_id)
        if href := sweep_response.get("job_href"):
            logger.info("Job link: %s", href)

        if wait_completion:
            return self.get_execution_result(job_id, context, verbose, wait_completion=True)
        else:
            return StationControlResult(sweep_id=job_id, task_id=job_id, status=TaskStatus.PENDING)

    def get_execution_result(
        self,
        job_id: uuid.UUID,
        context: dict[str, Any],
        verbose: bool = True,
        wait_completion: bool = True,
    ) -> StationControlResult:
        """Get execution results.

        Args:
            job_id: The ID of the job to process.
            context: Context object of the successful compiler run, containing the readout mappings.
            verbose: Whether to print results.
            wait_completion: If True, waits for job completion. If False, returns current status.

        Returns:
            The processed station control result.

        """
        sc_result = StationControlResult(sweep_id=job_id, task_id=job_id, status=TaskStatus.PENDING)

        try:
            if wait_completion:
                logger.info("Waiting for the job to finish...")

            while True:
                job_data = self._station_control.get_job(job_id)
                sc_result.status = TaskStatus.PENDING

                if job_data.job_status <= JobExecutorStatus.EXECUTION_STARTED:  # type: ignore[operator]
                    if wait_completion:
                        # Wait in the task queue while showing a progress bar
                        interrupted = self._station_control._wait_job_completion(  # type: ignore[attr-defined]
                            str(job_id), get_progress_bar_callback()
                        )
                        if interrupted:
                            raise KeyboardInterrupt
                    else:
                        # Non-blocking check - return current status
                        sc_result.status = (
                            TaskStatus.PROGRESS
                            if job_data.job_status == JobExecutorStatus.EXECUTION_STARTED
                            else TaskStatus.PENDING
                        )
                        return sc_result
                else:
                    # job is not in queue or executing, so we can query the sweep
                    result_or_nothing = self._get_result_of_started_job(
                        context, job_data, job_id, sc_result, wait_completion, verbose
                    )
                    if result_or_nothing is not None:
                        return result_or_nothing

                if wait_completion:
                    time.sleep(1)
                else:
                    break

        except KeyboardInterrupt as exc:
            if wait_completion:
                logger.info("Caught KeyboardInterrupt, revoking job %s", job_id)
                self._station_control.abort_job(job_id)
            raise KeyboardInterrupt from exc

        return sc_result

    def _get_result_of_started_job(
        self,
        context: dict[str, Any],
        job_data: Any,
        job_id: uuid.UUID,
        sc_result: StationControlResult,
        wait_completion: bool,
        verbose: bool,
    ) -> StationControlResult | None:
        sweep_data = self._station_control.get_sweep(job_id)
        if job_data.job_status == JobExecutorStatus.READY:
            if wait_completion:
                logger.info("Sweep status: %s", str(sweep_data.job_status))

            sc_result.status = TaskStatus.READY
            sc_result.result = map_sweep_results_to_logical_qubits(
                self._station_control.get_sweep_results(job_id),
                context["readout_mappings"],
                context["options"].heralding_mode,
            )
            sc_result.start_time = sweep_data.begin_timestamp.isoformat() if sweep_data.begin_timestamp else None
            sc_result.end_time = sweep_data.end_timestamp.isoformat() if sweep_data.end_timestamp else None

            if verbose and wait_completion:
                # TODO: Consider using just 'logger.debug' here and remove 'verbose'
                logger.info(sc_result.result)

            return sc_result

        if job_data.job_status == JobExecutorStatus.FAILED:
            sc_result.status = TaskStatus.FAILED
            sc_result.start_time = sweep_data.begin_timestamp.isoformat() if sweep_data.begin_timestamp else None
            sc_result.end_time = sweep_data.end_timestamp.isoformat() if sweep_data.end_timestamp else None
            sc_result.message = str(job_data.job_error)
            if wait_completion:
                logger.error("Submission failed! Error: %s", sc_result.message)
            return sc_result

        if job_data.job_status == JobExecutorStatus.ABORTED:
            sc_result.status = TaskStatus.FAILED
            sc_result.start_time = sweep_data.begin_timestamp.isoformat() if sweep_data.begin_timestamp else None
            sc_result.end_time = sweep_data.end_timestamp.isoformat() if sweep_data.end_timestamp else None
            sc_result.message = str(job_data.job_error)
            if wait_completion:
                logger.error("Submission was revoked!")
            return sc_result

        return None


init_loggers({"iqm": "INFO"})
