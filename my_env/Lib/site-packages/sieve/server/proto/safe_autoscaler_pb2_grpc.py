"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import safe_autoscaler_pb2 as safe__autoscaler__pb2


class SafeAutoscalerStub(object):
    """need 2 different services, all communications are started by the 'client', and we want asynchronous processing

    Run as server on the autoscaler, client on the worker pods
    Incoming KillMe messages should (along with whatever metadata updates) result in the deletion of `pod_name`
    A pod should send a KillMe request after receiving a StopWork request (blocking new tasks from being assigned) and completing its current tasks
    i.e. a pod should send a KillMe request when it is safe for the pod to be killed
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.KillMe = channel.unary_unary(
            "/rpc.SafeAutoscaler/KillMe",
            request_serializer=safe__autoscaler__pb2.KillMeRequest.SerializeToString,
            response_deserializer=safe__autoscaler__pb2.KillMeReply.FromString,
        )


class SafeAutoscalerServicer(object):
    """need 2 different services, all communications are started by the 'client', and we want asynchronous processing

    Run as server on the autoscaler, client on the worker pods
    Incoming KillMe messages should (along with whatever metadata updates) result in the deletion of `pod_name`
    A pod should send a KillMe request after receiving a StopWork request (blocking new tasks from being assigned) and completing its current tasks
    i.e. a pod should send a KillMe request when it is safe for the pod to be killed
    """

    def KillMe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_SafeAutoscalerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "KillMe": grpc.unary_unary_rpc_method_handler(
            servicer.KillMe,
            request_deserializer=safe__autoscaler__pb2.KillMeRequest.FromString,
            response_serializer=safe__autoscaler__pb2.KillMeReply.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.SafeAutoscaler", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class SafeAutoscaler(object):
    """need 2 different services, all communications are started by the 'client', and we want asynchronous processing

    Run as server on the autoscaler, client on the worker pods
    Incoming KillMe messages should (along with whatever metadata updates) result in the deletion of `pod_name`
    A pod should send a KillMe request after receiving a StopWork request (blocking new tasks from being assigned) and completing its current tasks
    i.e. a pod should send a KillMe request when it is safe for the pod to be killed
    """

    @staticmethod
    def KillMe(
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
            "/rpc.SafeAutoscaler/KillMe",
            safe__autoscaler__pb2.KillMeRequest.SerializeToString,
            safe__autoscaler__pb2.KillMeReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )


class JobManagerStub(object):
    """Run as a server on the worker pod, client on the server
    Incoming StopWork requests should be responded to by stopping task intake, waiting until in-progress tasks are complete, and sending a KillMe request
    The autoscaler should send a StopWork request when it has determined
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StopWork = channel.unary_unary(
            "/rpc.JobManager/StopWork",
            request_serializer=safe__autoscaler__pb2.StopWorkRequest.SerializeToString,
            response_deserializer=safe__autoscaler__pb2.StopWorkReply.FromString,
        )


class JobManagerServicer(object):
    """Run as a server on the worker pod, client on the server
    Incoming StopWork requests should be responded to by stopping task intake, waiting until in-progress tasks are complete, and sending a KillMe request
    The autoscaler should send a StopWork request when it has determined
    """

    def StopWork(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_JobManagerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "StopWork": grpc.unary_unary_rpc_method_handler(
            servicer.StopWork,
            request_deserializer=safe__autoscaler__pb2.StopWorkRequest.FromString,
            response_serializer=safe__autoscaler__pb2.StopWorkReply.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "rpc.JobManager", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class JobManager(object):
    """Run as a server on the worker pod, client on the server
    Incoming StopWork requests should be responded to by stopping task intake, waiting until in-progress tasks are complete, and sending a KillMe request
    The autoscaler should send a StopWork request when it has determined
    """

    @staticmethod
    def StopWork(
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
            "/rpc.JobManager/StopWork",
            safe__autoscaler__pb2.StopWorkRequest.SerializeToString,
            safe__autoscaler__pb2.StopWorkReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
