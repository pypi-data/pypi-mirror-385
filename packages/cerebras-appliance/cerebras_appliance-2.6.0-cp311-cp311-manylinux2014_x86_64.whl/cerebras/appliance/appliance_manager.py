# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""Class to manage interactions with appliance."""
import os
import shutil
import site
import sys
import textwrap
import threading
import time
from abc import ABC
from contextlib import contextmanager
from numbers import Real
from pathlib import Path
from typing import Iterable, List, Literal, Optional, Set, Tuple, Union

import grpc
import numpy as np
from tqdm import tqdm

from cerebras.appliance import __version__, log
from cerebras.appliance.appliance_client import (
    ApplianceClient,
    HeartBeatOptions,
)
from cerebras.appliance.cluster.client import (
    ClusterManagementClient,
    MountDir,
    UserSidecarEnv,
)
from cerebras.appliance.cluster.mount_volume import ClusterVolumeManager
from cerebras.appliance.cluster_config import ClusterConfig
from cerebras.appliance.environment import appliance_environ
from cerebras.appliance.errors import (
    ApplianceCompilationError,
    ApplianceDeadlockError,
    ApplianceDropModeComplete,
    ApplianceNanError,
    ApplianceResourceExhausted,
    ApplianceRuntimeJobTimeoutError,
    ApplianceUnknownError,
    ApplianceVersionError,
    ClusterJobInitError,
    ClusterJobScheduleError,
)
from cerebras.appliance.log import ClassLogger, named_class_logger
from cerebras.appliance.pb.framework.appliance_service_pb2 import (
    CheckCompileCompatibilityRequest,
    CheckCompileCompatibilityResponse,
    CompileRequest,
    CompileResponse,
    DeleteFromPTRRequest,
    FinalizeRequest,
    GetCMDStateRequest,
    GetFromPTRRequest,
    InitRequest,
    LoadRequest,
    MoveToPTRRequest,
    RunRequest,
)
from cerebras.appliance.pb.workflow.appliance.cluster_mgmt.cluster_pb2 import (
    CompileJobResponse,
    ComponentName,
    ImageBuildResponse,
    JobStatus,
)
from cerebras.appliance.pb.workflow.appliance.common.common_config_pb2 import (
    _CLUSTERDETAILS_TASKINFO_TASKTYPE,
    ClusterDetails,
    DebugArgs,
    ExecutionStrategy,
    FrameworkType,
    JobMode,
    LogSettings,
    ResourceInfo,
)
from cerebras.appliance.pb.workflow.appliance.common.message_queue_pb2 import (
    MsgStatus,
    ValidTopics,
)
from cerebras.appliance.utils import version_check
from cerebras.appliance.utils.debug_args import (
    update_debug_args_with_job_labels as update_job_labels,
)
from cerebras.appliance.utils.ini import set_ini
from cerebras.appliance.utils.pb_wrapper import common_config_wrapper
from cerebras.appliance.utils.pip import (
    get_package_path,
    pip_config_list,
    pip_freeze,
    pip_list,
)
from cerebras.appliance.utils.traceback import get_lowering_exception


@named_class_logger("ApplianceManager")
class ApplianceManager(ABC, ClassLogger):
    """Manage Appliance Interactions."""

    # Value to signal to client to send all weight tensors
    SEND_ALL_WGTS = "__123_send_all_weight_tensors_321__"

    # Flag that indicates if the initial checkpoint should be kept after
    # weights are sent to the appliance.
    _keep_initial_checkpoint = False

    def __init__(
        self,
        config: ClusterConfig,
        debug_args: DebugArgs,
        compile_dir: str,
        artifact_dir: str,
        framework_type: FrameworkType,
        op_profiler_config: Optional[LoadRequest.OpProfilerConfig] = None,
    ):
        super().__init__()
        self._compile_dir = Path(compile_dir)
        if self._compile_dir.is_absolute():
            self.logger.warning(
                "Passing an absolute path as the compile directory "
                "may lead to undesirably long paths as the directory "
                "is used on the server side, not on the client side. "
                "Please consider passing in a relative directory instead."
            )

        artifact_dir = Path(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        self._cluster_config = config
        self._framework_type = framework_type
        self._inference_mode = False
        self.output_names = []

        self._credentials = None
        self._certificate_bytes = None
        if self.credentials_path:
            self._set_credentials(Path(self.credentials_path).read_bytes())

        self._debug_args = self._init_debug_args(debug_args)

        self._coord_address = None
        self._default_authority = None
        self._grpc_client = None
        self._grpc_client_cv = threading.Condition()
        self._transfer_threads = 5

        if self.workflow_id is not None:
            self._debug_args.debug_mgr.workflow_id = self.workflow_id

        self._mgmt_client_args = {
            "server": self.mgmt_address,
            "crt_file": self.credentials_path,
            "namespace": self.mgmt_namespace,
            "job_timer": self.job_timer,
            "workdir": artifact_dir,
            "workflow_id": self.workflow_id,
            "cbcore_image": self.cbcore_image,
            "notifications": self.notifications,
        }

        self._skipped_weights = None
        self.recv_groups = []

        self._user_cv_path = None

        self._compile_resp = None
        self._prev_compile_resp = None
        self._cmd_state = None

        self._additional_mount_dirs = []
        self._additional_python_paths = []
        self._user_sidecar_env = None

        # Clean these up
        self.tracker_execute = None
        self._op_profiler_config = op_profiler_config

        if op_profiler_config:
            set_ini(
                self._debug_args,
                ws_perf_tsc_enable=True,
                ws_add_tsc_ctx_switch=True,
                ws_perf_tsc_number=30,
                profile_bins=True,
                profile_bins_filename="opprofiler_flow",
            )

        if not self._debug_args.debug_usr.disable_stall_detection:
            self.logger.verbose("Stall detection is enabled")
            set_ini(self._debug_args, ws_rt_enable_stall_check=True)

        # Log some settings to console
        self.logger.verbose(f"Credentials path: {self.credentials_path}")
        self.logger.debug(f"Debug args: {self._debug_args}")

    def __del__(self):
        if getattr(self, "_user_cv_path", None) is None:
            return
        if os.path.exists(self._user_cv_path):
            self.logger.info(
                f"Cleaning up user environment copy at {self._user_cv_path}"
            )
            shutil.rmtree(self._user_cv_path)

    def _init_debug_args(self, args: DebugArgs) -> DebugArgs:
        """Initialize job labels."""
        if not args:
            args = DebugArgs()
        if not args.debug_mgr:
            args.debug_mgr = DebugArgs.DebugMGR()
        if args.debug_mgr.labels is None:
            args.debug_mgr.labels = dict()
        update_job_labels(args, self.job_labels)

        # In release 1.9, the appliance heartbeat is moved from USR<->CRD to USR<->MGR.
        # USR<->CRD heartbeat will be disabled in 1.9 and be deprecated post 1.9.
        args.debug_crd.disable_heartbeat_check = True

        # For Release 2.0, we are disabling the Disk Mapping for large tensors by default
        # It needs to be enabled explicitly for now
        if not args.debug_crd.vlt_tensor_size_disk_rw:
            args.debug_crd.vlt_tensor_size_disk_rw = -1

        # If the strategy is seen as unspecified, it means the call was issued from an old client.
        if args.debug_mgr.message_broker_strategy == (
            DebugArgs.DebugMGR.MessageBrokerStrategy.MESSAGE_BROKER_STRATEGY_UNSPECIFIED
        ):
            args.debug_mgr.message_broker_strategy = (
                DebugArgs.DebugMGR.MessageBrokerStrategy.MESSAGE_BROKER_STRATEGY_ENABLED
            )

        # In Release 2.2, we introduced worker and user sidecar container separation.
        # Framework defines the resource separation between the two containers.
        args.debug_mgr.worker_sidecar.cpu_percent = 35
        args.debug_mgr.worker_sidecar.mem_percent = 65

        # In Release 2.5, we introduce weight and user sidecar container separation.
        # Framework defines the resource separation between the two containers.
        args.debug_mgr.weight_sidecar.cpu_percent = 20
        args.debug_mgr.weight_sidecar.mem_percent = 20

        # In Release 2.6, we introduce activation sidecar container separation.
        args.debug_mgr.activation_sidecar.cpu_percent = 20
        args.debug_mgr.activation_sidecar.mem_percent = 20

        args.debug_mgr.job_priority = self.job_priority

        if not args.debug_mgr.skip_nfs_mount_dir_check:

            def _assert_rwx_permissions(path):
                if (
                    not os.access(path, os.R_OK)
                    or not os.access(path, os.W_OK)
                    or not os.access(path, os.X_OK)
                ):
                    raise RuntimeError(
                        f"Mount directory {path} does not have read/write/execute permissions."
                    )

            if args.debug_mgr.nfs_workdir_logs_path:
                _assert_rwx_permissions(args.debug_mgr.nfs_workdir_logs_path)
            if args.debug_mgr.nfs_cached_compile_path:
                _assert_rwx_permissions(args.debug_mgr.nfs_cached_compile_path)
        return args

    def _set_credentials(self, value: bytes):
        """Sets the credentials from a certificate byte string."""
        if value:
            self._certificate_bytes = value
            self._credentials = grpc.ssl_channel_credentials(value)

    @property
    def compile_resp(self):
        """Compile response getter."""
        return self._compile_resp

    @compile_resp.setter
    def compile_resp(self, compile_resp):
        """Compile response setter."""
        self._prev_compile_resp = self._compile_resp
        self._compile_resp = compile_resp

    @property
    def cluster_config(self):
        """Returns the Cluster Config."""
        return self._cluster_config

    workflow_id = property(lambda self: self.cluster_config.workflow_id)
    mgmt_address = property(lambda self: self.cluster_config.mgmt_address)
    mgmt_namespace = property(lambda self: self.cluster_config.mgmt_namespace)
    credentials_path = property(
        lambda self: self.cluster_config.credentials_path
    )
    num_csx = property(lambda self: self.cluster_config.num_csx)
    max_wgt_servers = property(lambda self: self.cluster_config.max_wgt_servers)
    num_workers_per_csx = property(
        lambda self: self.cluster_config.num_workers_per_csx
    )
    max_act_per_csx = property(lambda self: self.cluster_config.max_act_per_csx)
    cbcore_image = property(lambda self: self.cluster_config.cbcore_image)
    job_labels = property(lambda self: self.cluster_config.job_labels)
    job_priority = property(lambda self: self.cluster_config.job_priority)
    job_timer = property(lambda self: self.cluster_config.job_timer)
    disable_version_check = property(
        lambda self: self.cluster_config.disable_version_check
    )
    notifications = property(lambda self: self.cluster_config.notifications)

    @property
    def mgmt_mount_dirs(self) -> List[MountDir]:
        """Returns list of mount directories to be mounted to the appliance."""
        return self.cluster_config.mount_dirs + self._additional_mount_dirs

    @property
    def mgmt_python_paths(self) -> List[str]:
        """Returns list of python paths to use for appliance workers."""
        return self.cluster_config.python_paths + self._additional_python_paths

    @property
    def grpc_client(self):
        """Client the FWK User Uses to connect to CRD."""
        with self._grpc_client_cv:
            if self._grpc_client is not None:
                return self._grpc_client

            self.logger.debug(
                f"Creating a framework GRPC client: {self._coord_address}, "
                f"with{'out' if self._credentials is None else ''} TLS, "
                f"{self._default_authority}"
            )

            heartbeat_options = None
            if not self._debug_args.debug_crd.disable_heartbeat_check:
                heartbeat_options = HeartBeatOptions()

            self._grpc_client = ApplianceClient(
                self._coord_address,
                credentials=self._credentials,
                default_authority=self._default_authority,
                execution_strategy=ExecutionStrategy.ES_WEIGHT_STREAMING,
                heartbeat_options=heartbeat_options,
                disable_version_check=self.disable_version_check,
                retry_small_payload=self._debug_args.debug_usr.retry_small_payload,
                max_transfer_bytes=self._debug_args.debug_usr.max_transfer_bytes,
            )
            self._grpc_client_cv.notify_all()
            return self._grpc_client

    def wait_for_grpc_client(self):
        """Waits for a grpc client to become available."""
        with self._grpc_client_cv:
            self._grpc_client_cv.wait_for(lambda: self._grpc_client is not None)

    def grpc_client_args(self):
        """
        Return a dict ready to be json serialized for creating a gRPC client
        on a remote host.
        """
        credentials = None
        if self._certificate_bytes:
            # PEM bytes are _already_ base64 encoded and is a safe ascii string
            credentials = self._certificate_bytes.decode("ascii")
        return {
            "crd_address": self._coord_address,
            "default_authority": self._default_authority,
            "credentials": credentials,
        }

    @property
    def skipped_weights(self) -> Set[str]:
        """Returns set of FW weights that are not needed by runtime.

        During lowering, some weights might be pruned from the graph. They exist
        and are needed for FW checkpoints, but are not needed by the runtime.
        We keep track of these during initialization and save them separately
        when saving checkpoints later on.
        """
        if self._skipped_weights is None:
            raise RuntimeError(
                "Attempting to access list of skipped weights, but weights "
                "have not been initialized yet."
            )
        return self._skipped_weights

    def remove_grpc_client(self):
        """Delete existing client to allow new connection."""
        with self._grpc_client_cv:
            if self._grpc_client is not None:
                self.logger.info(
                    f"Removing a framework GRPC client: {self._coord_address}"
                )
                self._grpc_client.close()
                del self._grpc_client
                self._grpc_client = None

    def _prep_cluster_details_resource(
        self, cluster_details: ClusterDetails, job_type: JobMode.Job
    ):
        """
        Updates resource requirements based on debug args.
        This is currently limited only to the coordinator role.

        Args:
            cluster_details: ClusterDetails object passed with at least 1 task.
            job_type: JobMode.Job enum which can be one of JobMode.COMPILE, JobMode.EXECUTE,
                JobMode.INFERENCE_COMPILE, JobMode.INFERENCE_EXECUTE.
        """
        # Cluster details memory and thread restrictions influenced
        # by debug args
        # Defaults are set during init/compile
        assert len(cluster_details.tasks) > 0, (
            f"Expected at least one task in cluster details when populating "
            f"resource info."
        )

        def task_type_str(enumval):
            return _CLUSTERDETAILS_TASKINFO_TASKTYPE.values_by_number[
                enumval
            ].name

        def bytes_str(b):
            if b == 0:
                return "unlimited"
            gi = b >> 30
            if gi > 0:
                return f"{int(gi)}Gi"
            mi = b >> 20
            if mi > 0:
                return f"{int(mi)}Mi"
            return f"{b} bytes"

        task_mode_override_map = {
            ClusterDetails.TaskInfo.TaskType.ACT: {
                JobMode.EXECUTE: self._debug_args.debug_usr.activation_resource,
                JobMode.INFERENCE_EXECUTE: self._debug_args.debug_usr.activation_resource,
            },
            ClusterDetails.TaskInfo.TaskType.BR: {
                JobMode.EXECUTE: self._debug_args.debug_usr.broadcastreduce_resource,
            },
            ClusterDetails.TaskInfo.TaskType.CHF: {
                JobMode.EXECUTE: self._debug_args.debug_usr.chief_resource,
                JobMode.INFERENCE_EXECUTE: self._debug_args.debug_usr.chief_resource,
            },
            ClusterDetails.TaskInfo.TaskType.CMD: {
                JobMode.EXECUTE: self._debug_args.debug_usr.command_resource,
            },
            ClusterDetails.TaskInfo.TaskType.CRD: {
                JobMode.COMPILE: self._debug_args.debug_usr.compile_coord_resource,
                JobMode.EXECUTE: self._debug_args.debug_usr.execute_coord_resource,
                JobMode.INFERENCE_COMPILE: self._debug_args.debug_usr.compile_coord_resource,
                JobMode.INFERENCE_EXECUTE: self._debug_args.debug_usr.execute_coord_resource,
            },
            ClusterDetails.TaskInfo.TaskType.WGT: {
                JobMode.EXECUTE: self._debug_args.debug_usr.weight_resource,
            },
            ClusterDetails.TaskInfo.TaskType.WRK: {
                JobMode.EXECUTE: self._debug_args.debug_usr.worker_resource,
            },
            ClusterDetails.TaskInfo.TaskType.KVSS: {
                JobMode.INFERENCE_EXECUTE: self._debug_args.debug_usr.kvss_resource,
            },
        }
        for task in cluster_details.tasks:
            if task.task_type not in task_mode_override_map:
                continue
            if job_type not in task_mode_override_map[task.task_type]:
                continue
            task_type = task_type_str(task.task_type)
            original = ResourceInfo()
            original.CopyFrom(task.resource_info)
            task.resource_info.MergeFrom(
                task_mode_override_map[task.task_type][job_type]
            )
            if task.resource_info.memory_bytes != original.memory_bytes:
                # When user sets override to < 0, they unset the limit entirely
                # allowing tasks of that replica type to use all node's memory
                task.resource_info.memory_bytes = max(
                    task.resource_info.memory_bytes, 0
                )
                old_mem = bytes_str(original.memory_bytes)
                new_mem = bytes_str(task.resource_info.memory_bytes)
                warning_msg = ""
                if task.resource_info.memory_bytes == 0:
                    warning_msg = str(
                        ". Warning: allowing unlimited memory usage can disrupt "
                        "other tasks on shared nodes!"
                    )
                self.logger.warning(
                    f"User override set for task {task_type} resource memory "
                    f"from {old_mem} to {new_mem}"
                    f"{warning_msg}"
                )

            if task.resource_info.cpu_millicore != original.cpu_millicore:
                # When user sets override to < 0, they unset the limit entirely.
                # Not showing a warning here as unlike memory, unlimited CPU is
                # less risky than unlimited memory
                task.resource_info.cpu_millicore = max(
                    task.resource_info.cpu_millicore, 0
                )
                self.logger.warning(
                    f"User override set for task {task.task_type} resource cpu from "
                    f"{original.cpu_millicore}m to {task.resource_info.cpu_millicore}m"
                )

            # unset upper bound if override is greater than requested memory or
            # requested memory is unset
            if (
                task.resource_info.memory_bytes == 0
                or task.resource_info.memory_bytes
                >= task.resource_info.memory_bytes_upper_bound
            ):
                task.resource_info.memory_bytes_upper_bound = 0

    def construct_debug_args(self) -> DebugArgs:
        """Constructs a DebugArgs object to be sent to the appliance."""
        debug_args = DebugArgs()
        debug_args.CopyFrom(self._debug_args)

        # Inject Appliance environment variables to be set by workers
        for k, v in appliance_environ.items():
            debug_args.debug_wrk.env_vars[k] = v

        return debug_args

    def request_execute_job(
        self,
        mgmt_client: ClusterManagementClient,
        compile_response: CompileResponse,
    ) -> dict:
        """Requests an allocation of resources to run on appliance.

        Args:
            mgmt_client: Client to communicate for resources.
            compile_response: Context from compilation that determines resources required.

        Returns:
            reponse: Protobuf message ExecuteJobResponse as a dict appended with the
                'certificate_bytes' field which the caller can use to configure the coordinator grpc
                channel.
        """
        cluster_details = common_config_wrapper(
            "ClusterDetails",
            compile_response.cluster_details,
            with_prefix_appliance=True,
        )
        execute_mode = JobMode.EXECUTE
        if self._inference_mode:
            execute_mode = JobMode.INFERENCE_EXECUTE
        self._prep_cluster_details_resource(cluster_details, execute_mode)

        debug_args = self.construct_debug_args()

        # Apply log settings for servers
        apply_wsc_log_settings("execute", debug_args)

        job_mode = JobMode(job=execute_mode, cluster_details=cluster_details)
        try:
            return mgmt_client.init_execute_job(
                str(self._compile_dir),
                compile_response.cache_compile_dir,
                job_mode,
                debug_args,
                mount_dirs=self.mgmt_mount_dirs,
                python_paths=self.mgmt_python_paths,
                user_sidecar_env=self._user_sidecar_env,
            )
        except (ClusterJobInitError, ClusterJobScheduleError) as e:
            mgmt_client.gather_cluster_job_failure(e.job_id)
            mgmt_client.cancel_job(e.job_id, JobStatus.JOB_STATUS_FAILED)
            raise

    def stage_execute_coordinator(self, resource_response: dict):
        """Prepares connection details for FWK<->CRD Communication.

        Args:
            resource_response: Cluster mgmt response message, as a dict.

        Returns:
            None
        """
        service_authority = resource_response["service_authority"]
        self.set_default_authority(service_authority)
        self.remove_grpc_client()
        self._update_coordinator_addr(resource_response["service_url"])
        self._set_credentials(resource_response["certificate_bytes"])
        # Make intial connection to provided coordinator
        self.grpc_client.ping()

    def set_default_authority(self, default_authority: Optional[str]):
        """Manage what authority is used in grpc client."""
        self._default_authority = default_authority

    def initialize_servers(self, init_request: Optional[InitRequest] = None):
        """Perform servers initialization."""
        self.grpc_client.monitor_error_async()
        with self.tracker_execute.entry("execute_init_request"):
            if init_request is None:
                init_request = InitRequest()
            self.grpc_client.init_servers(init_request)

    def initialize_session(
        self,
        run_request: RunRequest,
        compile_response: CompileResponse,
        drop_cmd_state: bool,
    ):
        """Perform initial connection handshake for execute mode.

        Args:
            run_request: Run request object.
            compile_response: Compile data from appliance.
            drop_cmd_state: Drop CMD state.
        """
        self.logger.info(f"Preparing to execute using {self.num_csx} CSX")
        self.grpc_client.monitor_error_async()
        with self.tracker_execute.entry("execute_load_request"):
            load_request = LoadRequest(
                cache_compile_dir=compile_response.cache_compile_dir,
                drop_cmd_state=drop_cmd_state,
            )

            if self._op_profiler_config:
                load_request.op_profiler_config.CopyFrom(
                    self._op_profiler_config
                )
            self.grpc_client.load_rtir(load_request)

        with self.tracker_execute.entry("execute_run_info"):
            self.grpc_client.run_deferred(run_request)

    def execute_session(
        self,
        initial_weights: Optional[dict] = None,
        skipped_weights: Optional[Set[str]] = None,
        has_modified_seed: Optional[bool] = None,
    ):
        """Perform initial connection handshake for execute mode.

        Args:
            initial_weights: The weight tensors to send.
            skipped_weights: Set of weights that are not needed by runtime.
            has_modified_seed: Indicates if seed has changed between sessions.
        """
        with self.tracker_execute.entry("execute_send_weights"):
            self.send_cmd_state(has_modified_seed)
            self.logger.info("About to send initial weights")
            # TODO: Move all "tracked" code to appliance.py
            # pylint: disable=no-member
            self.send_weights(
                initial_weights,
                skipped_weights,
            )
            self.logger.info("Finished sending initial weights")
        with self.tracker_execute.entry("execute_start_streaming"):
            self.logger.info("Finalizing appliance staging for the run")
            self.start_streaming()
            self.logger.info("Appliance staging is complete")

        self.logger.info("Beginning appliance run")

    def move_to_ptr(self, tensor_name: str, tensor_id: int) -> None:
        """Move a tensor to PTR which makes is available for the next session."""
        self.logger.debug(f"Moving to PTR {tensor_name=}, {tensor_id=}")
        request = MoveToPTRRequest(
            tensor_name=tensor_name,
            ptid=tensor_id,
        )
        self.grpc_client.move_to_ptr(request)

    def save_cmd_state(self):
        """Fetch CMD states from the appliance."""
        self._cmd_state = []
        cmd_state_ids = self.grpc_client.get_cmd_state_ids()
        for state_id in cmd_state_ids:
            self.logger.debug(f"Getting CMD state id: {state_id=}")
            request = GetCMDStateRequest(
                id=state_id,
            )
            state = self.grpc_client.get_cmd_state(request)
            self._cmd_state.append((state, state_id))

    def send_cmd_state(self, has_modified_seed):
        """Put the CMD state."""
        if not self._cmd_state:
            return

        if has_modified_seed:
            self.logger.debug(
                "PyTorch seed has changed between runs. Dropping CMD state."
            )
        else:
            for state, state_id in self._cmd_state:
                self.logger.debug(f"Sending CMD state id: {state_id=}")
                self._grpc_client.send_cmd_state(
                    state_id,
                    state,
                )

        # Clear the state after sending.
        self._cmd_state = None

    def get_from_ptr(
        self, tensor_id: int, keep_in_repo: bool = False
    ) -> np.ndarray:
        """Get a tensor from PTR."""
        self.logger.debug(f"Getting from PTR {tensor_id=}")
        request = GetFromPTRRequest(
            ptid=tensor_id,
            keep_in_repo=keep_in_repo,
        )
        return self.grpc_client.get_from_ptr(request)

    def delete_from_ptr(self, tensor_id: str) -> None:
        """Delete a tensor from PTR."""
        self.logger.debug(f"Deleting from PTR {tensor_id=}")
        request = DeleteFromPTRRequest(ptid=tensor_id)
        self.grpc_client.delete_from_ptr(request)

    def start_streaming(self):
        """Command to put Runtime in streaming mode."""
        self.grpc_client.sync()
        self.grpc_client.start_streaming()
        self.grpc_client.sync()

    def receive_activations(self, iteration):
        """Get activations from appliance."""
        return {
            output_name: self.receive_output(iteration, output_name)
            for output_name in self.output_names
        }

    def receive_output(self, iteration, name):
        """Get output from appliance."""
        return self.grpc_client.recv_output(iteration, name)

    def enable_inference_mode(self):
        """
        Set this appliance manager to inference mode.
        """
        self._inference_mode = True

    @contextmanager
    def compile_cluster(
        self,
    ) -> Union[ClusterManagementClient, CompileJobResponse]:
        """Context manager for requesting resource for a compile job."""
        # defaults to 0 which is no op currently (unlimited memory/cpu)
        # once restrictions are known, update the value
        if self._inference_mode:
            compile_memory_bytes = (
                30 << 30
            )  # current default ram memory for coord (~30 Gi for inference)
        else:
            compile_memory_bytes = (
                50 << 30
            )  # current default ram memory for coord (~50 Gi)
        compile_cpu_millicore = 24000  # current default num of cpus for coord
        cluster_details_compile = ClusterDetails()
        task_info = ClusterDetails.TaskInfo(
            task_type=ClusterDetails.TaskInfo.TaskType.CRD,
            resource_info=ResourceInfo(
                memory_bytes=compile_memory_bytes,
                cpu_millicore=compile_cpu_millicore,
            ),
        )
        compile_mode = JobMode.COMPILE
        if self._inference_mode:
            compile_mode = JobMode.INFERENCE_COMPILE
        cluster_details_compile.tasks.append(task_info)  # pylint: disable=E1101
        self._prep_cluster_details_resource(
            cluster_details_compile, compile_mode
        )
        job_mode = JobMode(
            job=compile_mode, cluster_details=cluster_details_compile
        )
        with ClusterManagementClient(**self._mgmt_client_args) as mgmt_client:
            try:
                mgmt_versions = mgmt_client.get_server_versions()
                # Handle in manager because cluster management test don't include appliance
                # SW-91475
            except grpc.RpcError as rpc_error:
                rpc_error_code = rpc_error.code()  # pylint: disable=no-member
                if rpc_error_code == grpc.StatusCode.UNIMPLEMENTED:
                    # Catch version 1.7 where we didn't have version checks
                    release_version = __version__.split("+")[0]
                    raise ApplianceVersionError(
                        "Cluster management server version is out of date. "
                        f"Please install version: {release_version}"
                    ) from rpc_error
                raise

            if not self.disable_version_check:
                # Prioritize checking against cluster management semantic version if exists
                if mgmt_client.is_cluster_semver_available():
                    mgmt_client.assert_compatible_cluster_software()
                else:
                    for component_details in mgmt_versions:
                        component_name = ComponentName.Name(
                            component_details.name
                        )
                        version = component_details.version
                        if "+" in version:
                            version, githash = version.split("+")
                        else:
                            # Possible future cluster version epoch.
                            # Definitely incompatible, so pass None for the githash
                            # to fail the check.
                            githash = None
                        version_check(component_name, version, githash)

            debug_args = DebugArgs()
            debug_args.CopyFrom(self._debug_args)

            # Apply log settings for servers
            apply_wsc_log_settings("compile", debug_args)

            debug_args.debug_crd.kvss_enabled = mgmt_client.is_kvss_available()

            try:
                response = mgmt_client.init_compile_job(
                    str(self._compile_dir),
                    job_mode,
                    debug_args,
                )
            except (ClusterJobInitError, ClusterJobScheduleError) as e:
                mgmt_client.gather_cluster_job_failure(e.job_id)
                mgmt_client.cancel_job(e.job_id, JobStatus.JOB_STATUS_FAILED)
                raise
            service_authority = response["service_authority"]
            self.set_default_authority(service_authority)

            self._update_coordinator_addr(response["service_url"])
            self._set_credentials(response["certificate_bytes"])
            # Refactor so client doesn't need to be returned
            yield mgmt_client, response

    def _update_coordinator_addr(self, addr: str):
        """Updates the coordinator addresses. Clients may attempt to connect to any of the
        addresses in the list."""

        # TODO workaround for mocking cluster management responses
        if addr.count(':') == 1:
            self._coord_address = addr
        else:
            second_colon_idx = addr.rfind(':')
            self._coord_address = addr[:second_colon_idx]

    def compile(self, compile_request: CompileRequest) -> CompileResponse:
        """Compiles the model for CS-X hardware.

        Args:
            compile_request: Compile information for appliance.

        Returns:
            compile_resp: Appliance response to compile request.
        """
        self.tracker_execute.start("compile_coord_start")

        with self.compile_cluster() as (mgmt_client, mgmt_response):
            self.remove_grpc_client()
            job_id = mgmt_response["job_id"]
            self.tracker_execute.stop("compile_coord_start")
            with self.tracker_execute.entry("cirh_end"), self.subscribe(
                ValidTopics.COMPILE
            ):
                exc = None
                try:
                    compile_dir_absolute_path = mgmt_response[
                        "compile_dir_absolute_path"
                    ]
                    compile_request.compile_dir = compile_dir_absolute_path
                    compile_resp = self.grpc_client.compile(compile_request)
                    cache_compile_dir = compile_resp.cache_compile_dir
                    mgmt_client.log_cache_compile(job_id, cache_compile_dir)
                    self.logger.info(
                        f"Compile artifacts successfully written to remote "
                        f"compile directory. Compile hash is: "
                        f"{os.path.basename(cache_compile_dir)}"
                    )
                except grpc.RpcError:
                    exc = sys.exc_info()[1]
                    if exc.code() == grpc.StatusCode.INTERNAL:
                        # Interpret as compilation error. Remove link to current exception
                        # so that it doesn't get printed when the raised exception is printed.
                        error = get_lowering_exception(exc.trailing_metadata())
                        if error is not None:
                            raise error from None  # pylint: disable=raising-bad-type
                        raise ApplianceCompilationError(exc.details()) from None
                    raise
                except Exception:  # pylint: disable=broad-except
                    exc = sys.exc_info()[1]
                    raise
                finally:
                    self.logger.debug("logging end time of compile job.")
                    mgmt_client.log_end_time(job_id)
                    if exc:
                        mgmt_client.gather_cluster_job_failure(job_id)
                    if self._grpc_client:
                        self.grpc_client.done()
                    if exc:
                        mgmt_client.cancel_job(
                            job_id, JobStatus.JOB_STATUS_FAILED, str(exc)
                        )

        self.compile_resp = compile_resp
        return compile_resp

    def check_compile_compatibility(self) -> CheckCompileCompatibilityResponse:
        """
        Check if new compile is compatible with the previous compile, so
        we can decide if we need to restart the appliance or not.
        """
        self.logger.debug(f"Checking compile compatibility")
        request = CheckCompileCompatibilityRequest(
            compile_resp=self._compile_resp,
            prev_compile_resp=self._prev_compile_resp,
        )
        return self.grpc_client.check_compile_compatibility(request)

    def copy_to(self, appliance: "ApplianceManager"):
        """Copy the appliance artifacts to another appliance instance."""

        # Сopy compile response.
        # pylint: disable=protected-access
        appliance._compile_resp = self._compile_resp
        appliance._prev_compile_resp = self._prev_compile_resp

        # Fetch CMD state from the appliance so we can propagate to the new
        # appliance execute job.
        self.save_cmd_state()
        # pylint: disable=protected-access
        appliance._cmd_state = self._cmd_state

    def configure_cluster_volumes(self, mgmt_client: ClusterManagementClient):
        """Configure all mount dirs and python paths for this run."""

        def _format_list(lst):
            return "  - " + "\n  - ".join(lst) + "\n"

        mount_dirs = set()
        pkg_python_paths = set()

        volume_manager = ClusterVolumeManager(mgmt_client.get_volumes())

        # Check if user-specified mount dirs are valid
        mount_errors = []
        for mount in self._cluster_config.mount_dirs:
            try:
                _ = volume_manager.get_mountpoint_for_path(mount.path)
            except Exception as e:  # pylint: disable=broad-except
                mount_errors.append((mount, str(e)))

        # Check if editable packages are in mountable locations
        pkg_errors = []
        for pkg in pip_list(editable=True):
            pkg_name = pkg["name"]
            pkg_loc = pkg["editable_project_location"]
            pkg_path = get_package_path(pkg_loc)
            if pkg_path is None:
                raise ValueError(
                    f"Unable to find the python path of editable package {pkg_name} with "
                    f"project location {pkg_loc} in the system's PYTHONPATH:"
                    f"{sys.path}."
                )

            # Always add the python path since we know we need it anyways
            pkg_python_paths.add(pkg_path)

            try:
                mount_dirs.add(volume_manager.get_mountpoint_for_path(pkg_path))
            except Exception as e:  # pylint: disable=broad-except
                pkg_errors.append((pkg_name, str(e)))

        # Either raise a warning or error if we found any issues in the mount paths
        if mount_errors or pkg_errors:
            error_str = ""
            if mount_errors:
                mount_error_str = ""
                for mount, error in mount_errors:
                    mount_error_str += (
                        f"\n  - mount_dir: {mount}\n    error: {error}"
                    )
                error_str += (
                    f"The following mount directories are not available to be mounted to "
                    f"the appliance:{mount_error_str}\n\n"
                )

            if pkg_errors:
                pkg_error_str = "".join(
                    f"\n  - name: {name}\n    error: {error}"
                    for name, error in pkg_errors
                )
                error_str += (
                    f"The following editable packages are not in a volume accessible to the "
                    f"cluster:{pkg_error_str}\n"
                    f"These editable packages must be on a mountable path so that the workers "
                    f"in the appliance can have access to them. Please ensure all editable "
                    f"packages are located under one of the available mountpoints.\n\n"
                )

            if volume_manager.available_mountpoints:
                error_str += (
                    f"Available mountpoints are:\n"
                    f"{_format_list(volume_manager.available_mountpoints)}"
                )
            else:
                error_str += (
                    "There does not seem to be any path available for mounting. "
                    "Please ensure that volumes available by cluster match mount paths "
                    "on the current system."
                )

            if self._cluster_config.disable_mount_check:
                self.logger.warning(error_str)
            else:
                raise RuntimeError(error_str)

        if self._cluster_config.mount_all:
            mount_dirs.update(volume_manager.available_mountpoints)

        # Add mount dirs
        for p in mount_dirs:
            mount = MountDir(path=p, container_path=p)
            if mount not in self.mgmt_mount_dirs:
                self._additional_mount_dirs.append(mount)

        # Add python paths
        for p in pkg_python_paths:
            if p not in self.mgmt_python_paths:
                self._additional_python_paths.append(p)

    def set_sidecar_image(self, image):
        """
        Update all the DebugArgs when sidecar image name is available.
        """
        self._debug_args.debug_mgr.worker_sidecar.image = image
        self._debug_args.debug_mgr.weight_sidecar.image = image
        self._debug_args.debug_mgr.activation_sidecar.image = image

    def get_sidecar_image(self):
        """
        Get the sidecar image reference.
        """
        if self._debug_args.debug_mgr.worker_sidecar.image:
            return self._debug_args.debug_mgr.worker_sidecar.image
        elif self._debug_args.debug_mgr.weight_sidecar.image:
            return self._debug_args.debug_mgr.weight_sidecar.image
        elif self._debug_args.debug_mgr.activation_sidecar.image:
            return self._debug_args.debug_mgr.activation_sidecar.image
        return ""

    @contextmanager
    def try_build_sidecar_image(self, timeout: Real = 60 * 60):
        """Trigger cluster management job to build sidecar image."""
        with ClusterManagementClient(**self._mgmt_client_args) as mgmt_client:
            start_time = time.time()

            # If there had been a job already created (from a different workflow) with the same
            # pip configs and package dependencies, we will reuse the same job.
            response = mgmt_client.init_image_build_job(
                debug_args=self._debug_args,
                pip_options=pip_config_list(),
                frozen_dependencies=pip_freeze(exclude_editable=True),
            )
            if response.mount_user_venv:
                self.logger.warning(
                    "User sidecar image build is disabled from server. "
                )
                yield
            else:
                self.set_sidecar_image(response.image_reference)
                yield
                success = self.wait_build_image(
                    mgmt_client, response, start_time, timeout
                )
                if not success:
                    self.logger.warning("Sidecar image build failed.")

    @contextmanager
    def build_worker_image(self, should_skip=False, timeout: Real = 60 * 60):
        """Trigger cluster management job to build worker image."""

        if should_skip:
            yield
            return

        with ClusterManagementClient(**self._mgmt_client_args) as mgmt_client:
            # Configure mount dirs and python paths
            if self.cluster_config.automount:
                try:
                    self.configure_cluster_volumes(mgmt_client)
                except Exception as e:
                    raise RuntimeError(
                        f"Auto-configuring mount_dirs and python_paths failed. See detailed error "
                        f"above for more details.\nTo skip auto-configuration, please set "
                        f"automount=False and manually specify mount_dirs and python_paths "
                        f"in the ClusterConfig."
                    ) from e

            if not self._debug_args.debug_usr.skip_image_build:
                start_time = time.time()

                # If there had been a job already created (from a different workflow) with the same
                # pip configs and package dependencies, we will reuse the same job.
                response = mgmt_client.init_image_build_job(
                    debug_args=self._debug_args,
                    pip_options=pip_config_list(),
                    frozen_dependencies=pip_freeze(exclude_editable=True),
                )

                if response.mount_user_venv:
                    if self._debug_args.debug_usr.skip_user_venv_mount:
                        raise RuntimeError(
                            "User sidecar image build is disabled from server and "
                            "venv mounting is explicitly disabled. It's not possible "
                            "to prepare the venv in the appliance. "
                        )
                    else:
                        self.logger.info(
                            "User sidecar image build is disabled from server. "
                            "Falling back to venv mounting."
                        )
                        self.copy_user_venv(mgmt_client)
                        yield
                else:
                    self.set_sidecar_image(response.image_reference)
                    yield
                    success = self.wait_build_image(
                        mgmt_client, response, start_time, timeout
                    )
                    if not success:
                        if self._debug_args.debug_usr.skip_user_venv_mount:
                            raise RuntimeError(
                                "User sidecar image build failed and "
                                "venv mounting is explicitly disabled. It's not possible "
                                "to prepare the venv in the appliance for the workers. "
                            )
                        else:
                            self.logger.info("Falling back to venv mounting.")
                            self.copy_user_venv(mgmt_client)
            elif not self._debug_args.debug_usr.skip_user_venv_mount:
                self.copy_user_venv(mgmt_client)
                yield
            else:
                raise RuntimeError(
                    "Both image build and venv mounting are disabled. "
                    "At least one must be enabled to be able to run "
                    "workers in the appliance."
                )

    def wait_build_image(
        self,
        mgmt_client: ClusterManagementClient,
        init_response: ImageBuildResponse,
        start_time: float,
        timeout: Real,
    ) -> bool:
        """Waits for image build to complete."""
        success = False
        if self.job_timer:
            self.job_timer.register_client(mgmt_client)
        wait_time = 0
        poll_interval = 5
        image_ready = init_response.image_ready
        job_id = init_response.job_id
        image_reference = init_response.image_reference
        while not image_ready and wait_time < timeout:
            response = mgmt_client.get_image_build_job(
                job_id=job_id, image_reference=image_reference
            )
            if response.status == JobStatus.JOB_STATUS_FAILED:
                break

            wait_time = time.time() - start_time
            time.sleep(poll_interval)
            image_ready = response.image_ready

        if response.status == JobStatus.JOB_STATUS_FAILED:
            error_log_path = mgmt_client.get_image_build_log_path()
            self.logger.error(
                f"Image build job {job_id} failed. "
                f"Please check the error log in {error_log_path}. "
            )
            self.set_sidecar_image("")
        elif not response.image_ready:
            self.logger.error(f"Image build job {job_id} timeout exceeded.")
            self.set_sidecar_image("")
        else:
            success = True
            if job_id:
                self.logger.info(f"Image build job {job_id} succeeded.")
            else:
                self.logger.info(
                    f"Image reference {response.image_reference} already exists."
                )

        return success

    def copy_user_venv(self, mgmt_client: ClusterManagementClient):
        """Copy user venv to the appliance."""
        # Set up additional mount dirs and python paths if we need to mount the user venv
        python_path = os.path.realpath(site.getsitepackages()[0])

        import cerebras.appliance

        # Gets the realpath of the source venv
        venv_src = Path(cerebras.appliance.__path__[0]).parents[3].resolve()

        (
            requires_venv_copy,
            cv_path,
        ) = mgmt_client.get_user_venv_cluster_volume_path(venv_src)
        if not requires_venv_copy:
            mount_dir = MountDir(
                path=str(venv_src), container_path=str(venv_src)
            )

            # TODO: Remove this special case handling in rel-2.7
            # In rel-2.5, we have introduced volume and mount deduplication in the
            # appliance backend. This means we should not need to special case
            # handling of the venv source path. We should always add it to the
            # mgmt_mount_dirs list.
            #
            # Legacy Note:
            # We only add venv_src to mgmt_mount_dirs if a prefix path doesn't
            # exist already. We have seen a case in ANL, where venv_src is located
            # under user's home directory, but not readable by root user when k8s
            # is doing the mount. The mount failed. See SW-115589 for details.
            # By not adding venv_src in that case avoid the mount failure.
            if not mgmt_client.is_mount_dir_dedupe_available():
                for md in self.mgmt_mount_dirs:
                    if str(venv_src).startswith(md.path):
                        mount_dir = None
                        break

            self._user_sidecar_env = UserSidecarEnv(
                mount_dir=mount_dir,
                python_path=python_path,
            )
        else:
            uid = os.getuid()
            process_id = os.getpid()
            venv_dst = f"{cv_path}/venv-{uid}-{process_id}"
            self.logger.info(
                f"Copying the user environment from {venv_src} to {venv_dst}"
            )

            if os.path.exists(venv_dst):
                self.logger.warning(
                    f"Deleting a stale venv {venv_dst} on the cluster volume"
                )
                shutil.rmtree(venv_dst)

            shutil.copytree(
                venv_src,
                venv_dst,
                dirs_exist_ok=False,
                copy_function=shutil.copy2,
                symlinks=True,
            )
            self._user_sidecar_env = UserSidecarEnv(
                mount_dir=MountDir(
                    path=str(venv_dst), container_path=str(venv_src)
                ),
                python_path=python_path,
            )

            self._user_cv_path = venv_dst

    @contextmanager
    def subscribe(self, topic: ValidTopics, timeout: int = 15):
        """Poll Message Queue topic until exit."""

        self.logger.debug(
            f"Subscribing to server topic {ValidTopics.Name(topic)}"
        )

        unsubscribe = threading.Event()
        client_kwargs = dict(
            crd_address=self._coord_address,
            credentials=self._credentials,
            default_authority=self._default_authority,
        )
        threading.Thread(
            target=poll_topic,
            args=(
                client_kwargs,
                (unsubscribe, self.grpc_client.shutdown),
                self.logger,
                topic,
                timeout,
            ),
            name=f"SubscribeThread:{topic}",
            daemon=True,
        ).start()

        try:
            yield
        finally:
            unsubscribe.set()
            self.logger.debug(
                f"Unsubscribed from server topic {ValidTopics.Name(topic)}"
            )

    @contextmanager
    def clean_shutdown(self, mgmt_client: ClusterManagementClient, job_id: str):
        """A context manager for cleanly shutting down the appliance."""
        run_state = None
        status = None
        exception = None

        try:
            yield
            status = JobStatus.JOB_STATUS_SUCCEEDED
            run_state = FinalizeRequest.FS_SUCCESS
        except (
            ApplianceDropModeComplete,
            ApplianceResourceExhausted,
            KeyboardInterrupt,
        ) as e:
            status = JobStatus.JOB_STATUS_CANCELLED
            exception = e
            self.logger.warning(f"Job {job_id} was cancelled due to {e}")
            raise
        except Exception as e:  # pylint: disable=broad-except
            status = JobStatus.JOB_STATUS_FAILED
            exception = e
            gather_failure = False
            if isinstance(e, ApplianceRuntimeJobTimeoutError):
                self.logger.error(
                    f"Initiating shutdown sequence due to job timeout: {e}"
                )
            elif isinstance(e, ApplianceDeadlockError):
                self.logger.error(
                    f"Initiating shutdown sequence due to Appliance deadlock: {e}"
                )
                run_state = FinalizeRequest.FS_STALL
                mgmt_client.log_debugviz_url(job_id)
            elif isinstance(e, ApplianceNanError):
                self.logger.error(
                    f"Initiating shutdown sequence due to NaN error: {e}"
                )
                run_state = FinalizeRequest.FS_NAN
            elif isinstance(e, grpc.RpcError):
                self.logger.error(
                    f"Initiating shutdown sequence due to gRPC error: {e}"
                )
                gather_failure = True
            elif isinstance(e, ApplianceUnknownError):
                self.logger.error(
                    f"Initiating shutdown sequence due to Appliance error: {e}"
                )
                gather_failure = True
            else:
                self.logger.error(
                    f"Initiating shutdown sequence due to error: {e}"
                )
                gather_failure = True
            if gather_failure:
                mgmt_client.gather_cluster_job_failure(job_id)

            raise
        finally:
            with self.tracker_execute.entry("execute_shutdown"):
                self.logger.debug(f"Logging end time of jobs {job_id}.")
                mgmt_client.log_end_time(job_id)
                if (
                    run_state is not None
                    and run_state != FinalizeRequest.FS_SUCCESS
                ):
                    try:
                        self.finalize(FinalizeRequest(state=run_state))
                    except Exception as e:  # pylint: disable=broad-except
                        self.logger.error(
                            f"Finalizing job ran into error: {e}.\n"
                            f"Continuing with shutdown sequence ..."
                        )

                # Clean shutdown when no errors
                if status != JobStatus.JOB_STATUS_FAILED:
                    try:
                        self.done()
                    except Exception as e:  # pylint: disable=broad-except
                        # If done() call throws an exception, ignore it and
                        # proceed with cancelling the job.
                        self.logger.error(
                            f"Clean shutdown ran into error: {e}.\n"
                            f"Proceeding to force cancel the job."
                        )
                self.grpc_client.shutdown.set()
                self.grpc_client.stop_heartbeat()
                # required to cleanup pods if not terminated yet
                message = "success" if exception is None else str(exception)
                mgmt_client.cancel_job(job_id, status, message)

                # log export upon stall
                if (
                    run_state == FinalizeRequest.FS_STALL
                    and mgmt_client.is_debug_volume_available()
                    and self._debug_args.debug_usr.auto_log_export_policy
                    != DebugArgs.DebugUSR.AutoLogExportPolicy.AUTO_LOG_EXPORT_POLICY_DISABLED
                ):
                    mgmt_client.request_log_export_debug_artifacts(job_id)

    def finalize(self, request: Optional[FinalizeRequest] = None):
        """Finalize the session on the appliance."""
        self.recv_groups = []
        self.grpc_client.stop_monitor_error()
        return self.grpc_client.finalize(
            request or FinalizeRequest(state=FinalizeRequest.FS_SUCCESS)
        )

    def done(self, wait: bool = False):
        """Cleanup appliance interaction."""
        if wait:
            # Call to done should never be creating a grpc client
            # If a call to done happens before a grpc client is created,
            # we should wait for the client to be created and before calling done
            self.wait_for_grpc_client()
        self.grpc_client.done()


def apply_wsc_log_settings(
    job_mode: Literal["compile", "execute"], debug_args: DebugArgs
) -> None:
    """Injects the WSC log settings to the given debug args.

    Args:
        job_mode: The job mode to apply the log settings for.
        debug_args: The debug args to inject log settings into.
    """

    log_settings = log.collect_wsc_log_settings()
    if not log_settings:
        return

    modes = log.WscLogSetting.allowed_modes()
    if job_mode not in modes:
        raise ValueError(
            f"Invalid job mode {job_mode}. Must be one of: {', '.join(modes)}"
        )

    for role in log.WscLogSetting.allowed_roles():
        role_args = getattr(debug_args, f"debug_{role}")
        role_log_settings = role_args.log_settings
        for log_setting in log_settings:
            if log_setting.mode is not None and log_setting.mode != job_mode:
                continue
            if log_setting.role is not None and log_setting.role != role:
                continue

            wsc_level = python_to_wsc_level(log_setting.level)
            if log_setting.tag is None:
                role_log_settings.global_level = wsc_level
            else:
                message_tag = role_log_settings.message_tags.add()
                message_tag.tag = log_setting.tag
                message_tag.level = wsc_level


def python_to_wsc_level(level: int) -> int:
    """Translate Client levels to Server Levels."""
    if level == log.NOTSET:
        return LogSettings.LogLevel.NOTSET
    if level <= log.TRACE:
        return LogSettings.LogLevel.TRACE
    if level <= log.DEBUG:
        return LogSettings.LogLevel.DEBUG
    if level <= log.VERBOSE:
        return LogSettings.LogLevel.VERBOSE
    if level <= log.INFO:
        return LogSettings.LogLevel.INFO
    if level <= log.WARNING:
        return LogSettings.LogLevel.WARNING
    if level <= log.ERROR:
        return LogSettings.LogLevel.ERROR
    if level <= log.FATAL:
        return LogSettings.LogLevel.FATAL
    return LogSettings.LogLevel.FATAL


def wsc_to_python_level(level: int) -> int:
    """Translate Server levels to Client Levels."""
    # Our proto levels are fixed and not ordered
    # so only do exact equality
    if level == LogSettings.LogLevel.NOTSET:
        return log.NOTSET
    if level == LogSettings.LogLevel.TRACE:
        return log.TRACE
    if level == LogSettings.LogLevel.DEBUG:
        return log.DEBUG
    if level == LogSettings.LogLevel.VERBOSE:
        return log.VERBOSE
    if level == LogSettings.LogLevel.INFO:
        return log.INFO
    if level == LogSettings.LogLevel.WARNING:
        return log.WARNING
    if level == LogSettings.LogLevel.ERROR:
        return log.ERROR
    if level == LogSettings.LogLevel.FATAL:
        return log.FATAL
    return log.FATAL


def poll_topic(
    client_kwargs: dict,
    stop_events: Iterable[threading.Event],
    logger: log._CerebrasLogger,
    topic: ValidTopics,
    timeout: int = 15,
):
    """Poll Server for messages in a topic queue and log results."""

    def is_done():
        return any(event.is_set() for event in stop_events)

    client = ApplianceClient(**client_kwargs, disable_version_check=True)
    pbar = None
    while not is_done():
        try:
            response = client.get_msg(topic, timeout)
        except grpc.RpcError as e:
            if is_done():
                break
            logger.debug(
                f"Polling topic {ValidTopics.Name(topic)} ran into error: {e} "
                f"Retrying ..."
            )
            time.sleep(1)
            continue

        # Do something with response (Assumes SINGLE PROGRESS BAR at a time)
        # 0. if empty continue
        if len(response.status.msg) == 0 and response.progress.total_steps == 0:
            # TODO probably want a non_empty bit for ease of use
            if pbar:
                # tqdm progress bar only updates when iteration changes
                # (there are settings that are intended to allow more frequent
                # updates, but they don't work as intended). So refresh even if
                # there are no updates.
                # Refresh interval = timeout
                pbar.refresh()
            continue
        # 1. if not in progress bar
        elif pbar is None:
            # a. response is progress: enter progress bar
            if response.progress.total_steps > 0:
                if sys.stdout.isatty():
                    pbar = tqdm(
                        total=response.progress.total_steps,
                        dynamic_ncols=True,  # Match console width
                        file=sys.stdout,
                        # Custom format:
                        # - Remove "n_fmt/total_fmt" as the step counts/units are
                        #   not for the user
                        # - Remove "remaining" time as it's quite misleading for
                        #   uneven iteration times
                        bar_format="{desc} {percentage:3.0f}%|{bar}| {elapsed} {postfix}",
                    )
                    pbar.set_description(response.progress.prefix)
                    if response.progress.postfix:
                        pbar.set_postfix(note=response.progress.postfix)
                    pbar.update(n=response.progress.step_increment)
                elif response.progress.current_step == 0:
                    # No progress bar if not tty. Only show message when the
                    # progress bar is initialized.
                    log_level = wsc_to_python_level(response.progress.tag.level)
                    logger.log(log_level, response.progress.prefix)
            # b. response is status: write to logger
            else:
                log_level, formatted_output = format_status(response.status)
                logger.log(log_level, formatted_output)
        # 2. in progress bar
        else:
            # a. response is progress: update bar
            if response.progress.total_steps > 0:
                pbar.set_description(response.progress.prefix)
                if response.progress.postfix:
                    pbar.set_postfix(note=response.progress.postfix)
                else:
                    pbar.set_postfix()
                pbar.update(n=response.progress.step_increment)
                # i. If total reached clear progress bar
                if pbar.n >= pbar.total:
                    pbar.close()
                    pbar = None

            # b. response is status: tqdm write (how does that interact with logger?)
            else:
                _, formatted_output = format_status(response.status)
                pbar.write(formatted_output)


def format_status(status: MsgStatus) -> Tuple[int, str]:
    """Display format for Message Queue."""
    log_level = wsc_to_python_level(status.tag.level)
    status_string = f"{status.msg}"
    if len(status.action) > 0:
        status_string = (
            status_string + "\n" + textwrap.indent(status.action, 3 * " ")
        )
    # TODO handle message tags and internal message content
    return log_level, status_string
