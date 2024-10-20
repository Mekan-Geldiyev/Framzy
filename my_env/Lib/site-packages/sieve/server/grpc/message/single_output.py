import cloudpickle
import sys
from ...proto import worker_pb2
from ..constants import MAX_OUTPUT_SIZE, WARNING_OUTPUT_SIZE
from ..serializer import add_type_converters


def get_single_output(output, file_handler, cost_handler):
    """
    This function gets the output from a user function, and returns it in a GRPC response.

    The output is checked for size, and is serialized and postprocessed. We then return it,
    upon which it will be sent over GRPC to the client.

    :param output: The output from the user's code
    :type output: Any
    :param handler: The handler to run postprocessing on the output
    :type handler: Handler
    """

    file_handler.postprocess(output)
    override_cost_dollars = cost_handler.reset_override_cost_dollars()
    output = add_type_converters(output)
    o = cloudpickle.dumps(output)
    if sys.getsizeof(o) > MAX_OUTPUT_SIZE:
        raise Exception(
            f"Output too large, must be less than {int(MAX_OUTPUT_SIZE / 1024 / 1024)} MB. Current size: {sys.getsizeof(o) / 1024 / 1024:.2f} MB. For large data, we strongly recommend using the sieve.File type: https://docs.sievedata.com/reference-v2/sdk/types/file."
        )
    if sys.getsizeof(o) > WARNING_OUTPUT_SIZE:
        print(
            f"WARNING: Output is large, we strongly recommend using the sieve.File type: https://docs.sievedata.com/reference-v2/sdk/types/file. Current size: {sys.getsizeof(o) / 1024 / 1024:.2f} MB. The maximum size is {int(MAX_OUTPUT_SIZE / 1024 / 1024)} MB."
        )
    return worker_pb2.PredictionResponse(
        data=o,
        status=worker_pb2.Status.STATUS_SUCCEEDED,
        stop=True,
        metadata=worker_pb2.PredictionMetadata(
            override_cost_dollars=override_cost_dollars
        ),
    )
