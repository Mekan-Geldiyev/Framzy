import traceback
from ...proto import worker_pb2


class InternalInputException(Exception):
    pass


class WorkerNotSetupException(Exception):
    pass


def get_error_response(e: Exception):
    """Check if e is system exit in case we want to exit the process and raise an exception"""

    print("Prediction failed", str(e))
    o = traceback.format_exc()
    return worker_pb2.PredictionResponse(
        status=worker_pb2.Status.STATUS_FAILED, error=str(o), data=b"", stop=True
    )


def get_fatal_response(e: Exception):
    """Check if e is system exit in case we want to exit the process and raise an exception"""

    print("Prediction failed", str(e))
    o = traceback.format_exc()
    return worker_pb2.PredictionResponse(
        status=worker_pb2.Status.STATUS_FAILED,
        error=str(o),
        data=b"",
        stop=True,
        fatal=True,
    )
