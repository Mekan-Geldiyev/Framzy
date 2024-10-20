"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import server_pb2 as server__pb2


class OutputServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOutputs = channel.unary_stream(
            "/rpc.OutputService/GetOutputs",
            request_serializer=server__pb2.GetOutputsRequest.SerializeToString,
            response_deserializer=server__pb2.Output.FromString,
        )


class OutputServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOutputs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_OutputServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetOutputs": grpc.unary_stream_rpc_method_handler(
            servicer.GetOutputs,
            request_deserializer=server__pb2.GetOutputsRequest.FromString,
            response_serializer=server__pb2.Output.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.OutputService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class OutputService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOutputs(
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
            "/rpc.OutputService/GetOutputs",
            server__pb2.GetOutputsRequest.SerializeToString,
            server__pb2.Output.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )


class FileServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetFile = channel.unary_unary(
            "/rpc.FileService/GetFile",
            request_serializer=server__pb2.GetFileRequest.SerializeToString,
            response_deserializer=server__pb2.File.FromString,
        )
        self.GetFileStream = channel.unary_stream(
            "/rpc.FileService/GetFileStream",
            request_serializer=server__pb2.GetFileStreamRequest.SerializeToString,
            response_deserializer=server__pb2.FileChunk.FromString,
        )


class FileServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetFileStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_FileServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetFile": grpc.unary_unary_rpc_method_handler(
            servicer.GetFile,
            request_deserializer=server__pb2.GetFileRequest.FromString,
            response_serializer=server__pb2.File.SerializeToString,
        ),
        "GetFileStream": grpc.unary_stream_rpc_method_handler(
            servicer.GetFileStream,
            request_deserializer=server__pb2.GetFileStreamRequest.FromString,
            response_serializer=server__pb2.FileChunk.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.FileService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class FileService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetFile(
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
            "/rpc.FileService/GetFile",
            server__pb2.GetFileRequest.SerializeToString,
            server__pb2.File.FromString,
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
    def GetFileStream(
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
            "/rpc.FileService/GetFileStream",
            server__pb2.GetFileStreamRequest.SerializeToString,
            server__pb2.FileChunk.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
