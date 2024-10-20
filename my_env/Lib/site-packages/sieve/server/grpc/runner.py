"""
This file defines the runner abstraction.

This entails running the user code, handling the inputs and outputs,
and propogating any errors that happen in the user code.
"""

import sys
import traceback
from enum import Enum
from typing import Any, Optional
import time
from ..proto import worker_pb2
from sieve.functions.function import get_inputs, get_output_type
from ..logging.logging import (
    StdoutCapturing,
    StderrCapturing,
    get_sieve_internal_logger,
)
import sys
from ..handling.file_handling import Handler, get_global_handler as get_file_handler
from ..handling.cost_handling import get_global_handler as get_cost_handler
from ..handling.sys_handling import is_sigterming, run_lock
from .message import (
    get_iterator_inputs,
    get_iterator_outputs,
    get_single_output,
    get_single_inputs,
    get_error_response,
    get_fatal_response,
    InternalInputException,
)
import time
import os
from subprocess import Popen, PIPE
import grpc
import json


class FatalException(Exception):
    pass


class PostProcessingException(Exception):
    pass


class NoValidGPUException(Exception):
    pass


logger = get_sieve_internal_logger()


def check_gpu():
    """
    This function checks if there are any GPUs available on the machine.

    This is to be run if the user requests a GPU to ensure the machine is valid.
    """

    p = Popen(
        [
            "nvidia-smi",
            "--query-gpu=index,uuid,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode,temperature.gpu",
            "--format=csv,noheader,nounits",
        ],
        stdout=PIPE,
    )
    stdout, stderror = p.communicate()
    output = stdout.decode("UTF-8")
    lines = output.split(os.linesep)
    num_devices = len(lines) - 1
    logger.info(f"found {num_devices} gpus")
    for line in lines:
        if "Unknown Error" in line or "N/A" in line:
            raise NoValidGPUException("GPU found with unknown error.")
    return num_devices


class PredictionRunner:
    """
    This class wraps around the user code, and handles the setup and prediction.

    Additionally, we define functions for input serialization and deserialization,
    as well as output serialization and deserialization. We also handle any errors
    that happen for setup and predict, returning a serialized error message to the
    GRPC client. We also log any errors that happen in the user code.

    For logging, we surround the user code runs with custom loggers that allow
    us to expose these to the user later on Sieve.
    """

    PROCESSING_DONE = 1
    EXIT_SENTINEL = "exit"

    class OutputType(Enum):
        NOT_STARTED = 0
        SINGLE = 1
        GENERATOR = 2

    def __init__(
        self,
        predict_timeout: Optional[int] = None,
        predictor=None,
        config=None,
        model_id=None,
        instance_id=None,
    ) -> None:
        self.predict_timeout = predict_timeout
        self.config = config
        self.predictor = predictor

        # TODO: Make the below less hardcoded
        if config["type"] == "model":
            self.predictor_inputs = get_inputs(self.predictor._get_function())
            self.predictor_outputs = get_output_type(self.predictor._get_function())
        else:
            self.predictor_inputs = get_inputs(self.predictor)
            self.predictor_outputs = get_output_type(self.predictor)
        self.setup_failed = False
        self.setup_failed_exception = ""
        self.iter_input = config["is_iterator_input"]
        self.iter_output = config["is_iterator_output"]
        self.model_id = model_id
        self.instance_id = instance_id
        self.metadata = {
            "model_id": self.model_id,
            "instance_id": self.instance_id,
        }

        pod_id = os.getenv("PL_POD_NAME", "")
        if pod_id:
            self.metadata["pod_id"] = pod_id

        self.file_handler = get_file_handler()
        self.cost_handler = get_cost_handler()
        self.setup_status = worker_pb2.SetupStatus.SETUP_UNKNOWN
        self.setup_error = ""
        self.setup_time = 0
        self.wait_for_gpu_time = 0
        self.setup_logs = []
        self.first_job_after_setup = True

    def set_metadata(self, metadata):
        self.metadata = metadata

    def set_file_cache_url(self, file_cache_url):
        self.file_handler.set_file_server_url(file_cache_url)

    def set_file_cache_headers(self, file_cache_headers):
        self.file_handler.set_file_server_headers(file_cache_headers)

    def get_setup_status(self):
        return self.setup_status

    def get_setup_time(self):
        return self.setup_time

    def wait_for_gpu(self):
        try:
            s = time.time()
            timeout = 60
            logger.info("Waiting for GPU availability")
            while check_gpu() < 1 and time.time() - s < timeout:
                logger.info("no gpus available, waiting")
                time.sleep(1)
            if check_gpu() < 1:
                raise NoValidGPUException("No GPU detected")
            logger.info(f"gpu availability check complete in {time.time() - s} seconds")
            self.wait_for_gpu_time = time.time() - s
        except NoValidGPUException as e:
            if is_sigterming():
                logger.info("waiting for gpu failed due to SIGTERM, raising")
                sys.exit(1)
            # Check if e is system exit in case we want to exit the process and raise an exception
            logger.info(f"wait for gpu failed {str(e)}")
            self.setup_status = worker_pb2.SetupStatus.SETUP_NODE_ERROR
            tb = traceback.format_exc()
            self.setup_error = f"Error: {e} \n Traceback: {tb}"
            self.setup_failed = True
            self.setup_failed_exception = f"Error: {e} \n Traceback: {tb}"
            self.wait_for_gpu_time = time.time() - s
            logger.info(tb)
            return False
        return True

    def setup(self):
        """
        This function sets up the user code.

        If there is no setup function, it will basically be a no-op.
        On error, we return a serialized error message to the GRPC client,
        which will be logged on Sieve.
        """

        self.metadata["stage"] = "setup"
        with StdoutCapturing(self.metadata, runner=self), StderrCapturing(
            self.metadata, runner=self
        ):
            try:
                s = time.time()
                logger.info("Setting up predictor @ " + str(s))
                if self.config["type"] == "model":
                    self.predictor = self.predictor()
                logger.info(f"Predictor setup complete in {time.time() - s} seconds")
                self.setup_status = worker_pb2.SetupStatus.SETUP_SUCCESS
                self.setup_time = time.time() - s
            except Exception as e:
                if is_sigterming():
                    logger.info("Setup failed due to SIGTERM, raising")
                    sys.exit(1)
                # Check if e is system exit in case we want to exit the process and raise an exception
                logger.info(f"Setup failed {str(e)}")
                tb = traceback.format_exc()
                logger.info(f"Setup failed traceback {tb}")
                self.setup_status = worker_pb2.SetupStatus.SETUP_ERROR
                self.setup_error = f"Error: {e} \n Traceback: {tb}"
                self.setup_failed = True
                self.setup_failed_exception = f"Error: {e} \n Traceback: {tb}"
                self.setup_time = time.time() - s
                logger.info(s)

    def predict(self, request: Any):
        """
        This function takes a GRPC request, converts it to the necessary inputs, runs the prediction, and returns or yields the output.

        If there is an error, we return a serialized error message to the GRPC client and exit the streams.
        If there is a SIGTERM, we raise an exception to exit the process.
        If there is a client disconnect, we raise an exception to exit the process.
        We handle the inputs and outputs differently according to if they are iterators or not,
        calling the necessary postprocessing handler which handles the serialization of the output.
        """

        self.cost_handler.reset_override_cost_dollars()

        try:
            with run_lock:
                if self.setup_failed:
                    raise Exception("Setup failed: " + self.setup_failed_exception)

                # Print setup logs again with associated job ID
                if self.first_job_after_setup:
                    for log in self.setup_logs:
                        log["metadata"]["job_id"] = self.metadata.get("job_id", "")
                        print(f"<sieve>{json.dumps(log)}</sieve>")
                    self.first_job_after_setup = False

                self.metadata["stage"] = "run"  # For grouping run logs together
                with StdoutCapturing(self.metadata), StderrCapturing(self.metadata):
                    logger.info("Running a user prediction")
                    if self.iter_input:
                        formatted_input_iterators = get_iterator_inputs(
                            self.predictor_inputs, request, self.file_handler
                        )
                        output = self.predictor(**formatted_input_iterators)
                    else:
                        inputs = get_single_inputs(
                            self.predictor_inputs, request, self.file_handler
                        )
                        output = self.predictor(**inputs)

                    # Postprocess output
                    if self.iter_output:
                        o = get_iterator_outputs(
                            output, self.file_handler, self.cost_handler
                        )
                        for i in o:
                            yield i
                    else:
                        yield get_single_output(
                            output, self.file_handler, self.cost_handler
                        )
                    logger.info("Finished user prediction")

        except SystemExit as e:
            if is_sigterming():
                logger.info("Prediction failed due to SIGTERM, raising")
                sys.exit(1)
        except InternalInputException as e:
            logger.info("Prediction failed due to SIGTERM caught by Iterator, raising")
            sys.exit(1)
        except grpc.RpcError as e:
            s = traceback.format_exc()
            logger.info(
                f"Prediction failed due to client disconnecting {e}, raising\n traceback: {s}"
            )
            with StdoutCapturing(self.metadata), StderrCapturing(self.metadata):
                traceback.print_exc()
                yield get_error_response(e)
        except FatalException as e:
            with StdoutCapturing(self.metadata), StderrCapturing(self.metadata):
                traceback.print_exc()
                yield get_fatal_response(e)
        except Exception as e:
            with StdoutCapturing(self.metadata), StderrCapturing(self.metadata):
                traceback.print_exc()
                yield get_error_response(e)
