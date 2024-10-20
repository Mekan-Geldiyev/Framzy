from queue import Queue
import sys
import cloudpickle
from threading import Thread
from ..constants import MAX_INPUT_SIZE
import grpc
from ...handling.sys_handling import is_sigterming
from queue import Empty
from ..serializer import input_to_type
from ...logging.logging import get_sieve_internal_logger
from .error_response import InternalInputException
import traceback

logger = get_sieve_internal_logger()


class SimpleIterator:
    """
    This class is an iterator we pass in to user functions, that wraps around a stream of data.

    We use a queue to listen asynchronously for data, and when it's present and the user requests it,
    we return it. We have a lot of error handling code here to make sure that we don't block the user, but
    also are not blocked in the even of a SIGTERM. We loop every 10 seconds so we're not infinitely blocked.
    """

    EXIT_SENTINEL = None

    def __init__(self, input, handler):
        self.queue = Queue()
        self.input = input
        self.handler = handler

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                out = self.queue.get(
                    block=True, timeout=10
                )  # Timeout to check if we should terminate, non-blocking
                break
            except Empty:
                pass
        # Check if out is of type InternalInputException
        if issubclass(type(out), InternalInputException):
            logger.info(
                f"Iterator Received InternalInputException: {out} on key: {self.input['name']}"
            )
            raise out
        if out is self.EXIT_SENTINEL:
            logger.info(f"Iterator Received exit sentinel on key: {self.input['name']}")
            raise StopIteration

        logger.info(f"Iterator Received data on key: {self.input['name']}")
        logger.debug(f"Iterator Received data: {out} on key: {self.input['name']}")
        # Check if inputs are too large
        if sys.getsizeof(out) > MAX_INPUT_SIZE:
            raise Exception("Input size too large: ", sys.getsizeof(out), "bytes")
        pre = cloudpickle.loads(out)
        input_type = self.input.get("type", None)
        pre = input_to_type(pre, input_type)
        self.handler.preprocess(pre)
        return pre


class AsyncStreamToIterators:
    """
    This class is responsible for listening to the stream of data from the client, and sending it to the correct iterator.

    For all messages we get in the request stream, we check if it's a stop message, and if so, we send a stop message to the
    correct iterator. If we get a kill message, we send a kill message to all iterators. Otherwise, we send the data to the
    correct iterator. We use a thread-safe queue to send the data to the iterator, so that we can asynchronously listen for data
    and not block the user.
    """

    def __init__(self, request, iterators):
        """
        :param request: The request from the client
        :type request: worker_pb2.PredictionRequest
        :param iterators: The iterators to send data to based on key
        :type iterators: Dict[str, SimpleIterator]
        """
        self.request = request
        self.iterators = iterators

    def run(self):
        stops_received = 0
        try:
            for message in self.request:
                logger.info(f"AsyncStream Received message: {message}")
                if message.kill:
                    logger.info("AsyncStream Received kill request")
                    for iterator in self.iterators.values():
                        iterator.queue.put(InternalInputException("Worker killed"))
                    return
                if message.stop:
                    logger.info(
                        f"AsyncStream Received stop message on key: {message.key}"
                    )
                    stops_received += 1
                    self.iterators[message.key].queue.put(SimpleIterator.EXIT_SENTINEL)
                    if stops_received >= len(self.iterators):
                        break
                else:
                    logger.info(f"AsyncStream Received data on key: {message.key}")
                    self.iterators[message.key].queue.put(message.data)
        except (grpc.RpcError, KeyError) as e:
            s = traceback.format_exc()
            logger.info(
                f"Error in AsyncStream, potentially due to client disconnecting, exiting: {str(e)}"
            )
            logger.info(f"Traceback: {s}")
            logger.info(f"Error type: {type(e)}")
            for iterator in self.iterators.values():
                iterator.queue.put(InternalInputException("Client disconnected"))
            return


def get_iterator_inputs(predictor_inputs, request, handler):
    """ "
    This function takes in the predictor inputs, the request, and the handler, and returns a dictionary of iterators.

    We pass these iterators as inputs into the user code prediction function, so that the user can iterate over the data
    from the input streams.
    """

    input_iterators = {i["name"]: SimpleIterator(i, handler) for i in predictor_inputs}
    async_stream_to_iterators = AsyncStreamToIterators(request, input_iterators)

    t = Thread(target=async_stream_to_iterators.run)
    t.start()
    return input_iterators
