"""
This file defines the GRPC service abstractions.

These entail wrapping around proto definitions for a GRPC
service that handles setup and monitoring the health of a 
worker, and a GRPC service that handles job requests after
the setup is finished, propogating errors back to the client.
There is also a main function that starts the GRPC server.
"""

import time
import datetime
from ..handling.sys_handling import is_sigterming
import sys
import os
import grpc
import json
import traceback
import concurrent.futures
from ..proto import worker_pb2, worker_pb2_grpc
from sieve.functions.utils import load
from .worker import queue_worker_from_argv
import concurrent.futures
from ..handling import sys_handling
from ..logging.logging import (
    get_sieve_internal_logger,
    StdoutCapturing,
    StderrCapturing,
)
from .message.error_response import get_error_response, WorkerNotSetupException
import uuid

logger = get_sieve_internal_logger()


class WorkerHealthGRPCServicer(worker_pb2_grpc.WorkerHealthServicer):
    """
    This class implements the WorkerHealthServicer interface defined in the proto file.
    This services the GRPC server to trigger setup for functions, and send health status updates.
    """

    def __init__(self, worker, worker_load_error, *args, **kwargs):
        """
        :param worker: Worker that wraps around user code
        :type worker: GRPCWorker
        :param worker_load_error: Error that occurred while loading the worker
        """
        self.worker = worker
        self.worker_load_error = worker_load_error
        super().__init__(*args, **kwargs)

    def Check(self, request, context):
        if request.kill:
            sys_handling.default_sigterm_handler("KILL", None)
        time.sleep(0.1)
        if self.worker_load_error is not None:
            return self.LoadError()

        return worker_pb2.HealthCheckResponse(
            status=self.worker.get_health(), setup_info=self.worker.get_setup_info()
        )

    def LoadError(self):
        logger.info("Returning load error to health check")
        return worker_pb2.HealthCheckResponse(
            status=worker_pb2.HealthStatus.HEALTH_ERROR,
            setup_info=worker_pb2.Setup(
                status=worker_pb2.SetupStatus.SETUP_LOAD_ERROR,
                retries=0,
                time=0,
                error=self.worker_load_error,
            ),
        )

    def Watch(self, request, context):
        logger.info("Got watch request")
        if request.kill:
            logger.info("got kill request")
            sys_handling.default_sigterm_handler("KILL", None)

        # Check if worker failed to load via importlib, and return error if so.
        if self.worker_load_error is not None:
            yield self.LoadError()
            return

        while True:
            breaking = False
            cur_health = self.worker.get_health()
            if cur_health == worker_pb2.HealthStatus.HEALTH_SERVING:
                breaking = True
            yield worker_pb2.HealthCheckResponse(
                status=cur_health, setup_info=self.worker.get_setup_info()
            )
            if breaking:
                logger.info("Setup complete")
                break
            time.sleep(0.1)


class JobWorkerGRPCServicer(worker_pb2_grpc.JobWorkerServicer):
    """
    This class implements the JobWorkerServicer interface defined in the proto file.
    This services the GRPC server to handle job requests. To be run after the worker finishes setup.
    """

    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        super().__init__(*args, **kwargs)

    def WorkRequest(self, request, context):
        try:
            if hasattr(request, "kill") and request.kill:
                logger.info("got kill request")
                sys_handling.default_sigterm_handler("KILL", None)
                return
            if self.worker is None:
                logger.info("Worker is None, shutting down (assuming kill request)")
                sys_handling.default_sigterm_handler("KILL", None)
                return

            if self.worker.get_health() != worker_pb2.HealthStatus.HEALTH_SERVING:
                logger.info("Worker can't serve prediction, sending error response")
                context.set_details("Worker not serving")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                yield get_error_response(WorkerNotSetupException("Worker not serving"))
                return

            logger.info("WorkRequest called")

            out = self.worker.handle(request, context)
            logger.info("WorkRequest yielding")
            for o in out:
                yield o
        except grpc.RpcError as e:
            logger.info(f"gRPC connection broken during WorkRequest: {e}")
            sys_handling.default_sigterm_handler("KILL", None)


def main(*, host="0.0.0.0", port="50054", health_port="50055"):
    """
    This function is the main function for the GRPC server. It starts the health server, and then the main server.
    Along the way, it loads the worker, and calls the setup function.

    :param host: Host to run the server on
    :type host: str
    :param port: Port to run the main server on
    :type port: int
    :param health_port: Port to run the setup/initialization server on
    :type health_port: int
    """
    global server
    if os.getenv("GRPC_PORT"):
        port = os.getenv("GRPC_PORT")
    else:
        print("GRPC port not specified, using default")
    if os.getenv("HEALTH_CHECK_PORT"):
        health_port = os.getenv("HEALTH_CHECK_PORT")
    else:
        print("health check port not specified, using default")

    worker, worker_metadata, worker_error = get_worker()

    model_id = worker_metadata["model_id"]
    pod_id = worker_metadata["pod_id"]

    logger.profile(
        message="initialize grpc server",
        period="start",
        metadata={
            "model_id": model_id,
            "pod_id": pod_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            ),
        },
    )
    options = [
        ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ("grpc.max_receive_message_length", 50 * 1024 * 1024),
    ]
    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=1), options=options
    )
    worker_pb2_grpc.add_WorkerHealthServicer_to_server(
        WorkerHealthGRPCServicer(worker=worker, worker_load_error=worker_error), server
    )
    worker_pb2_grpc.add_JobWorkerServicer_to_server(
        JobWorkerGRPCServicer(worker=worker), server
    )

    server.add_insecure_port(f"{host}:{health_port}")
    server.add_insecure_port(f"{host}:{port}")

    sys_handling.server = server

    server.start()
    logger.info(f"Health server started on {host}:{health_port}")
    logger.info(f"Main server started on {host}:{port}, same backend as health server")
    logger.profile(
        message="initialize grpc server",
        period="end",
        metadata={
            "model_id": model_id,
            "pod_id": pod_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            ),
        },
    )

    logger.info(f"Main server started on {host}:{port}")

    if worker_error is not None:
        logger.info(f"Error loading model: {worker_error}, skipping setup func")
    else:
        logger.profile(
            message="setup",
            period="start",
            metadata={
                "model_id": model_id,
                "pod_id": pod_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S,%f"
                ),
            },
        )
        worker.setup()
        logger.info("Finished worker setup")
        logger.profile(
            message="setup",
            period="end",
            metadata={
                "model_id": model_id,
                "pod_id": pod_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S,%f"
                ),
            },
        )

    logger.info(f"Server ready for prediction")
    server.wait_for_termination()


def get_worker():
    """
    This function loads the worker from the model_id and config_json passed in as arguments to the script.
    It then creates a queue worker from the loaded worker, and returns it.

    :return: Worker that wraps around user code
    :rtype: GRPCWorker
    """
    instance_id = str(uuid.uuid4())
    [model_id, config_json] = sys.argv[1:]
    config = json.loads(config_json)
    predictor = None

    metadata = {
        "model_id": model_id,
        "instance_id": instance_id,
        "stage": "load",  # For grouping load (import, etc.) together
    }

    logger.info("Starting worker load")

    pod_id = os.getenv("PL_POD_NAME", "unknown")
    logger.profile(
        message="import user code",
        period="start",
        metadata={
            "model_id": model_id,
            "pod_id": pod_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            ),
        },
    )

    worker_metadata = {
        "model_id": model_id,
        "instance_id": instance_id,
        "pod_id": pod_id,
    }

    try:
        with StdoutCapturing(metadata=metadata), StderrCapturing(metadata=metadata):
            predictor = load(config)
    except Exception as e:
        if is_sigterming():
            sys.exit(1)
        load_error = str(e) + "\n" + traceback.format_exc()
        logger.info(f"Error loading model: {load_error}")
        return None, worker_metadata, load_error
    worker = queue_worker_from_argv(
        predictor, model_id=model_id, config=config, instance_id=instance_id
    )
    logger.info("Finished worker load")
    logger.profile(
        message="import user code",
        period="end",
        metadata={
            "model_id": model_id,
            "pod_id": pod_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            ),
        },
    )
    return worker, worker_metadata, None


if __name__ == "__main__":
    main()
