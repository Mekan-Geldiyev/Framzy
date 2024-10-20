"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import autoscale_pb2 as autoscale__pb2


class AutoscalerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RequestAutoscale = channel.unary_unary(
            "/autoscale.Autoscaler/RequestAutoscale",
            request_serializer=autoscale__pb2.ScalingRequest.SerializeToString,
            response_deserializer=autoscale__pb2.ScalingResponse.FromString,
        )


class AutoscalerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RequestAutoscale(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_AutoscalerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "RequestAutoscale": grpc.unary_unary_rpc_method_handler(
            servicer.RequestAutoscale,
            request_deserializer=autoscale__pb2.ScalingRequest.FromString,
            response_serializer=autoscale__pb2.ScalingResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "autoscale.Autoscaler", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class Autoscaler(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RequestAutoscale(
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
            "/autoscale.Autoscaler/RequestAutoscale",
            autoscale__pb2.ScalingRequest.SerializeToString,
            autoscale__pb2.ScalingResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
