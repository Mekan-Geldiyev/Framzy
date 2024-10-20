import cloudpickle
import sys
from ...proto import worker_pb2
from ..constants import MAX_OUTPUT_SIZE, WARNING_OUTPUT_SIZE
from ..serializer import add_type_converters

import threading
from queue import Queue, Empty
from ...logging.logging import get_sieve_internal_logger

logger = get_sieve_internal_logger()

ONE_YEAR = 365 * 24 * 60 * 60

THREAD_DONE = object()


class LazyThreadPoolExecutor(object):
    """
    This class is a lazy thread pool executor that allows us to run a function on a thread pool

    The purpose of this class is so that we can run postprocessing on the outputs users submit,
    so we can handle things like serialization, type conversion, and output size checking.
    """

    def __init__(self, num_workers=1):
        self.num_workers = num_workers
        self.result_queue = Queue()
        self.thread_sem = threading.Semaphore(num_workers)
        self.threading_lock = threading.Lock()
        self.active_threads = 0
        self._shutdown = threading.Event()
        self.threads = []

    def map(self, predicate, iterable):
        self._shutdown.clear()
        self.iterable = ThreadSafeIterator(iterable)
        self._start_threads(predicate)
        return self._result_iterator()

    def shutdown(self, wait=True):
        self._shutdown.set()
        if wait:
            for t in self.threads:
                t.join()

    def _start_threads(self, predicate):
        for i in range(self.num_workers):
            t = threading.Thread(
                name="LazyChild #{0}".format(i), target=self._make_worker(predicate)
            )
            t.daemon = True
            self.threads.append(t)
            t.start()

    def _make_worker(self, predicate):
        def _w():
            with self.threading_lock:
                self.active_threads += 1
            with self.thread_sem:
                try:
                    for idx, thing in self.iterable:
                        out = predicate(thing)
                        with self.threading_lock:
                            self.result_queue.put((idx, out))
                            if self._shutdown.is_set():
                                break
                except Exception as e:
                    self.result_queue.put((-1, e))
                    logger.debug(f"putting exception {str(e)}")
            with self.threading_lock:
                self.active_threads -= 1
                self.result_queue.put((-1, THREAD_DONE))
                logger.debug("putting done")

        return _w

    def _result_iterator(self):
        buffer = {}
        expected_idx = 0
        while 1:
            # Queue.get is not interruptable w/ ^C unless you specify a
            # timeout.
            # Hopefully one year is long enough...
            # See http://bugs.python.org/issue1360
            try:
                result = self.result_queue.get(block=True, timeout=10)
            except Empty:
                continue

            result_idx, result = result

            if issubclass(type(result), Exception):
                raise result
            if result is not THREAD_DONE:
                buffer[result_idx] = result
                while expected_idx in buffer:
                    yield buffer.pop(expected_idx)
                    expected_idx += 1
            else:
                # Check if thread is done with lock than purge remainder of queue.
                with self.threading_lock:
                    if self.active_threads == 0:
                        # Check result_queue again to make sure we didn't miss anything
                        while self.result_queue.qsize() > 0:
                            logger.debug(
                                f"queue size remainder {str(self.result_queue.qsize())}"
                            )
                            try:
                                result = self.result_queue.get(block=False)
                                result_idx, result = result
                                if issubclass(type(result), Exception):
                                    raise result
                                if result is not THREAD_DONE:
                                    buffer[result_idx] = result
                                    while expected_idx in buffer:
                                        yield buffer.pop(expected_idx)
                                        expected_idx += 1
                                else:
                                    logger.debug("got thread done in final iter")
                            except Empty:
                                logger.debug("queue empty")
                                break

                        if self.result_queue.qsize() > 0:
                            logger.debug(
                                f"queue size remainder AFTER yield {str(self.result_queue.qsize())}"
                            )
                        if len(buffer) > 0:
                            logger.debug(
                                f"buffer size remainder AFTER yield {str(len(buffer))}"
                            )

                        logger.debug("thread done and no other threads active")
                        return
                    else:
                        logger.debug("thread done but other threads still active")
                        continue


class ThreadSafeIterator(object):
    def __init__(self, it):
        self._it = iter(it)
        self.lock = threading.Lock()
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            ret_idx = self.idx
            self.idx += 1
            return ret_idx, self._it.__next__()


def get_iterator_outputs(output, file_handler, cost_handler):
    """
    This function is responsible for running postprocessing on the stream users yield.

    It runs postprocessing on the outputs, and then serializes and checks for size.
    It maps over the iterator using a thread pool executor, so that we can run postprocessing
    in parallel with the user's code. We yield the outputs after postprocessing so they
    can be synchronously fed back to the client.

    :param output: The output from the user's code
    :type output: Iterator[Any]
    :param handler: The handler to run postprocessing on the outputs
    :type handler: Handler
    """

    def process(iterator_output_result):
        file_handler.postprocess(iterator_output_result)
        override_cost_dollars = cost_handler.get_override_cost_dollars()
        iterator_output_result = add_type_converters(iterator_output_result)
        encoded_output = cloudpickle.dumps(iterator_output_result)
        if sys.getsizeof(encoded_output) > MAX_OUTPUT_SIZE:
            raise Exception(
                f"Output too large, must be less than {int(MAX_OUTPUT_SIZE / 1024 / 1024)} MB. Current size: {sys.getsizeof(encoded_output) / 1024 / 1024:.2f} MB. For large data, we recommend using the sieve.File type: https://docs.sievedata.com/reference-v2/sdk/types/file."
            )
        if sys.getsizeof(encoded_output) > WARNING_OUTPUT_SIZE:
            print(
                f"WARNING: Output is large, we strongly recommend using the sieve.File type: https://docs.sievedata.com/reference-v2/sdk/types/file. Current size: {sys.getsizeof(encoded_output) / 1024 / 1024:.2f} MB. The maximum size is {int(MAX_OUTPUT_SIZE / 1024 / 1024)} MB."
            )
        processed_output = worker_pb2.PredictionResponse(
            data=encoded_output,
            status=worker_pb2.Status.STATUS_SUCCEEDED,
            stop=False,
            metadata=worker_pb2.PredictionMetadata(
                override_cost_dollars=override_cost_dollars
            ),
        )
        return processed_output

    executor = LazyThreadPoolExecutor(8)
    for processed_output in executor.map(process, output):
        yield processed_output
    executor.shutdown()
    override_cost_dollars = cost_handler.reset_override_cost_dollars()
    yield worker_pb2.PredictionResponse(
        data=b"",
        status=worker_pb2.Status.STATUS_SUCCEEDED,
        stop=True,
        metadata=worker_pb2.PredictionMetadata(
            override_cost_dollars=override_cost_dollars
        ),
    )
