import sys
import cloudpickle
from ..constants import MAX_INPUT_SIZE, WARNING_INPUT_SIZE
import grpc
from ...logging.logging import get_sieve_internal_logger
from .error_response import InternalInputException
from ...handling import sys_handling
from ..serializer import input_to_type

logger = get_sieve_internal_logger()


def get_single_inputs(predictor_inputs, request, handler):
    """
    This function gets inputs from a request, and returns them in a dictionary.

    The inputs are checked for size, and are deserialized and preprocessed.
    We will then pass them into a function as args or kwargs. We check to
    make sure that the client doesn't disconnect while we're waiting for inputs.
    We also check to make sure the number of inputs is correct.

    :param predictor_inputs: List of inputs the user function takes
    :type predictor_inputs: List[Dict[str, Any]]
    :param request: The GRPC request
    :type request: Iterator[worker_pb2.Input]
    :param handler: The handler to run preprocessing on the inputs
    :type handler: Handler
    """

    inputs_dict = {i["name"]: i for i in predictor_inputs}
    inputs = {}
    try:
        for message in request:
            if len(inputs_dict) == 0:
                raise Exception("Too many inputs")
            if message.kill:
                logger.info("Got kill request")
                sys_handling.default_sigterm_handler("KILL", None)
            if message.key not in inputs_dict:
                raise Exception("Invalid input name: " + message.key)
            if sys.getsizeof(message.data) > MAX_INPUT_SIZE:
                raise Exception(
                    f"Input too large, must be less than {int(MAX_INPUT_SIZE / 1024 / 1024)} MB. Current size: {sys.getsizeof(message.data) / 1024 / 1024:.2f} MB. For large data, we recommend using the sieve.File type: https://docs.sievedata.com/reference-v2/sdk/types/file."
                )
            if sys.getsizeof(message.data) > WARNING_INPUT_SIZE:
                print(
                    f"WARNING: Input is large, we strongly recommend using the sieve.File type: https://docs.sievedata.com/reference-v2/sdk/types/file. Current size: {sys.getsizeof(message.data) / 1024 / 1024:.2f} MB. The maximum size is {int(MAX_INPUT_SIZE / 1024 / 1024)} MB."
                )
            pre = cloudpickle.loads(message.data)
            input_type = inputs_dict[message.key].get("type", None)
            pre = input_to_type(pre, input_type)
            handler.preprocess(pre)
            inputs[message.key] = pre
            inputs_dict.pop(message.key)
            if len(inputs_dict) == 0:
                break
    except (grpc.RpcError, KeyError) as e:
        logger.info(
            "Error in get_single_inputs, potentially due to client disconnecting, exiting"
        )
        raise InternalInputException("Client disconnected")

    if len(inputs_dict) > 0:
        raise Exception("Too few inputs")

    return inputs
