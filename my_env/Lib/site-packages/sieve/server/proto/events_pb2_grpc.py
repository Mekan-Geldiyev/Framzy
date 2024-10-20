"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import events_pb2 as events__pb2


class EventProcessorStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ProcessEvent = channel.unary_unary(
            "/event.EventProcessor/ProcessEvent",
            request_serializer=events__pb2.Event.SerializeToString,
            response_deserializer=events__pb2.EventStatus.FromString,
        )


class EventProcessorServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ProcessEvent(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_EventProcessorServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "ProcessEvent": grpc.unary_unary_rpc_method_handler(
            servicer.ProcessEvent,
            request_deserializer=events__pb2.Event.FromString,
            response_serializer=events__pb2.EventStatus.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "event.EventProcessor", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class EventProcessor(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ProcessEvent(
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
            "/event.EventProcessor/ProcessEvent",
            events__pb2.Event.SerializeToString,
            events__pb2.EventStatus.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
