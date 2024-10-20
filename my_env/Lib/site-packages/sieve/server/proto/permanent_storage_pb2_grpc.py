"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import permanent_storage_pb2 as permanent__storage__pb2


class PermanentStorageWorkerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Check = channel.unary_unary(
            "/rpc.PermanentStorageWorker/Check",
            request_serializer=permanent__storage__pb2.StorageRequest.SerializeToString,
            response_deserializer=permanent__storage__pb2.StorageResponse.FromString,
        )


class PermanentStorageWorkerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Check(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_PermanentStorageWorkerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Check": grpc.unary_unary_rpc_method_handler(
            servicer.Check,
            request_deserializer=permanent__storage__pb2.StorageRequest.FromString,
            response_serializer=permanent__storage__pb2.StorageResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.PermanentStorageWorker", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class PermanentStorageWorker(object):
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
            "/rpc.PermanentStorageWorker/Check",
            permanent__storage__pb2.StorageRequest.SerializeToString,
            permanent__storage__pb2.StorageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
