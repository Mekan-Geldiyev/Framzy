"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import worker_pb2 as worker__pb2


class JobWorkerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.WorkRequest = channel.stream_stream(
            "/rpc.JobWorker/WorkRequest",
            request_serializer=worker__pb2.PredictionInput.SerializeToString,
            response_deserializer=worker__pb2.PredictionResponse.FromString,
        )


class JobWorkerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def WorkRequest(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_JobWorkerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "WorkRequest": grpc.stream_stream_rpc_method_handler(
            servicer.WorkRequest,
            request_deserializer=worker__pb2.PredictionInput.FromString,
            response_serializer=worker__pb2.PredictionResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.JobWorker", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class JobWorker(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def WorkRequest(
        request_iterator,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            "/rpc.JobWorker/WorkRequest",
            worker__pb2.PredictionInput.SerializeToString,
            worker__pb2.PredictionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )


class WorkerHealthStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Check = channel.unary_unary(
            "/rpc.WorkerHealth/Check",
            request_serializer=worker__pb2.HealthCheckRequest.SerializeToString,
            response_deserializer=worker__pb2.HealthCheckResponse.FromString,
        )
        self.Watch = channel.unary_stream(
            "/rpc.WorkerHealth/Watch",
            request_serializer=worker__pb2.HealthCheckRequest.SerializeToString,
            response_deserializer=worker__pb2.HealthCheckResponse.FromString,
        )


class WorkerHealthServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Check(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Watch(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_WorkerHealthServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Check": grpc.unary_unary_rpc_method_handler(
            servicer.Check,
            request_deserializer=worker__pb2.HealthCheckRequest.FromString,
            response_serializer=worker__pb2.HealthCheckResponse.SerializeToString,
        ),
        "Watch": grpc.unary_stream_rpc_method_handler(
            servicer.Watch,
            request_deserializer=worker__pb2.HealthCheckRequest.FromString,
            response_serializer=worker__pb2.HealthCheckResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.WorkerHealth", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class WorkerHealth(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Check(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/rpc.WorkerHealth/Check",
            worker__pb2.HealthCheckRequest.SerializeToString,
            worker__pb2.HealthCheckResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Watch(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/rpc.WorkerHealth/Watch",
            worker__pb2.HealthCheckRequest.SerializeToString,
            worker__pb2.HealthCheckResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
