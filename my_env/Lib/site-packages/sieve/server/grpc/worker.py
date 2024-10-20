"""
This file defines the worker abstraction.

This entails registering any metadata for a request
before the runner can pass it through user code.
"""

import json
import os
import sys
import time
from typing import Any, Dict, Optional
from ..proto import worker_pb2
from sieve.functions.function import _Function
import json
import uuid
from ..env.env import set_env_vars, reset_env_vars
from .runner import PredictionRunner
import traceback

from ..logging.logging import get_sieve_internal_logger

logger = get_sieve_internal_logger()


class GRPCWorker:
    """
    This class wraps around the runner, which wraps around the user code.

    This class handles metadata passed in, like env vars setting and unsetting,
    allowing the runner to focus on the user code and I/O.
    """

    SETUP_TIME_QUEUE_SUFFIX = "-setup-time"
    RUN_TIME_QUEUE_SUFFIX = "-run-time"
    STAGE_SETUP = "setup"
    STAGE_RUN = "run"

    def __init__(
        self,
        predictor: Any,
        model_id: Optional[str] = None,
        predict_timeout: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        instance_id: Optional[str] = None,
    ):
        self.runner = PredictionRunner(
            predict_timeout=predict_timeout,
            predictor=predictor,
            config=config,
            model_id=model_id,
            instance_id=instance_id,
        )
        self.instance_id = instance_id
        self.model_id = model_id
        self.config = config
        self.should_exit = False
        self.health = worker_pb2.HealthStatus.HEALTH_UNKNOWN

    def setup(self):
        """Setup the worker, including setting up the runner and waiting for GPU if necessary."""

        self.health = worker_pb2.HealthStatus.HEALTH_SETUP
        if self.config["gpu"] == "true":
            gpu_found = self.runner.wait_for_gpu()
            if not gpu_found:
                self.health = worker_pb2.HealthStatus.HEALTH_ERROR
                return

        self.runner.setup()
        self.health = worker_pb2.HealthStatus.HEALTH_SERVING

    def get_setup_info(self):
        """Get the setup info for the worker, including the setup status, retries, time, and error."""
        response = worker_pb2.Setup(
            status=self.runner.get_setup_status(),
            retries=0,
            time=self.runner.get_setup_time(),
            error=self.runner.setup_failed_exception,
        )
        return response

    def get_health(self):
        return self.health

    def format_metadata(self, grpc_metadata):
        """
        Format metadata from the GRPC request into a dictionary of run metadata and a dictionary of environment variables.

        This is so user code can access important metadata about the run,
        like the run ID, job ID, and workflow ID.
        """
        job_id = grpc_metadata.get("job_id", "")
        run_id = grpc_metadata.get("run_id", "")
        workflow_id = grpc_metadata.get("workflow_id", "")
        organization_id = grpc_metadata.get("organization_id", "")
        workflow_name = grpc_metadata.get("workflow_name", "")
        env_vars_json = grpc_metadata.get("env", "{}")
        env_vars = json.loads(env_vars_json)
        run_metadata = {
            "run_id": run_id,
            "job_id": job_id,
            "workflow_id": workflow_id,
            "organization_id": organization_id,
            "model_id": self.model_id,
            "instance_id": self.instance_id,
        }
        pod_id = os.getenv("PL_POD_NAME", "")
        if pod_id:
            run_metadata["pod_id"] = pod_id

        env_vars["SIEVE_RUN_ID"] = run_id
        env_vars["SIEVE_JOB_ID"] = job_id
        env_vars["SIEVE_WORKFLOW_ID"] = workflow_id
        env_vars["SIEVE_ORGANIZATION_ID"] = organization_id
        env_vars["SIEVE_MODEL_ID"] = self.model_id
        env_vars["SIEVE_WORKFLOW_NAME"] = workflow_name
        return run_metadata, env_vars

    def get_file_cache_url(self, grpc_metadata) -> str:
        return grpc_metadata.get("file_server_url", "")

    def get_file_cache_headers(self, grpc_metadata) -> Dict:
        fch_json = grpc_metadata.get("file_server_headers", "{}")
        return json.loads(fch_json)

    def handle(
        self,
        request: Any,
        context: Any,
    ) -> None:
        """
        This function takes in a request and context, and handles the request by passing it to the runner.

        Before passing it to the runner, it formats the metadata and sets the environment variables.
        After passing it to the runner, it unsets the environment variables.
        """

        try:
            metadata = dict(context.invocation_metadata())
            run_metadata, env_vars = self.format_metadata(metadata)
            file_cache_url = self.get_file_cache_url(metadata)
            file_cache_headers = self.get_file_cache_headers(metadata)

            # Populate meta-information for job
            self.runner.set_metadata(run_metadata)
            self.runner.set_file_cache_url(file_cache_url)
            self.runner.set_file_cache_headers(file_cache_headers)

            # Set env vars
            original_env_vars = set_env_vars(env_vars)
        except Exception as e:
            s = traceback.format_exc()
            logger.info(s)
            logger.info("Error in handle: {}".format(e))

        _Function.upload = False
        out = self.runner.predict(request)
        logger.profile(
            "prediction",
            period="start",
            metadata={
                "model_id": self.model_id,
                "job_id": metadata.get("job_id", ""),
            },
        )
        for o in out:
            yield o
        logger.profile(
            "prediction",
            period="end",
            metadata={
                "model_id": self.model_id,
                "job_id": metadata.get("job_id", ""),
            },
        )

        # Unset env vars
        try:
            reset_env_vars(env_vars, original_env_vars)
        except Exception as e:
            s = traceback.format_exc()
            logger.info(s)
            logger.info("Error in handle: {}".format(e))


def queue_worker_from_argv(
    predictor: Any,
    model_id: str,
    config: Dict[str, Any],
    instance_id: str = None,
) -> GRPCWorker:
    """
    Construct a GRPCWorker object from sys.argv, taking into account optional arguments and types.

    This is intensely fragile. This should be kwargs or JSON or something like that.
    """

    predict_timeout_int = None
    _Function.upload = True
    worker = GRPCWorker(
        predictor,
        model_id=model_id,
        predict_timeout=predict_timeout_int,
        config=config,
        instance_id=instance_id,
    )
    _Function.upload = False
    return worker
