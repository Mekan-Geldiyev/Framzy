"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import billing_pb2 as billing__pb2


class BillingManagerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RequestBilling = channel.unary_unary(
            "/billing.BillingManager/RequestBilling",
            request_serializer=billing__pb2.BillingRequest.SerializeToString,
            response_deserializer=billing__pb2.BillingResponse.FromString,
        )


class BillingManagerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RequestBilling(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_BillingManagerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "RequestBilling": grpc.unary_unary_rpc_method_handler(
            servicer.RequestBilling,
            request_deserializer=billing__pb2.BillingRequest.FromString,
            response_serializer=billing__pb2.BillingResponse.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "billing.BillingManager", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class BillingManager(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RequestBilling(
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
            "/billing.BillingManager/RequestBilling",
            billing__pb2.BillingRequest.SerializeToString,
            billing__pb2.BillingResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
