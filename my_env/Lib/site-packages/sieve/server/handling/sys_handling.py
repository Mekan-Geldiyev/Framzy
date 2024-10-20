"""
This module handles system level operations for Sieve.

This includes handling SIGTERM and handling run synchronization.
"""

import signal
import os
import threading
from ..logging.logging import get_sieve_internal_logger

logger = get_sieve_internal_logger()

SIGTERMING = False
server = None

run_lock = threading.Lock()

from contextlib import contextmanager


@contextmanager
def get_run_lock_timeout(timeout):
    result = run_lock.acquire(timeout=timeout)
    try:
        yield result
    finally:
        if result:
            run_lock.release()


def default_sigterm_handler(signum, frame):
    """Default sigterm handler for init handling"""

    logger.info("shutting down...")
    if server is not None:
        logger.info("stopping server")
    global SIGTERMING
    SIGTERMING = True
    # Check if grpc connections are still active
    if signum == "KILL":
        logger.info("Received GRPC request to terminate self, exiting")
        if server:
            server.stop(1)
            logger.info("stopped server")
            server.wait_for_termination()
            logger.info("server terminated")
    else:
        with get_run_lock_timeout(3600 * 24):
            if server:
                server.stop(3600 * 24)
                logger.info("stopped server")
                server.wait_for_termination(3600 * 24)
                logger.info("server terminated")
    logger.info("Exiting")
    os._exit(0)


def is_sigterming():
    return SIGTERMING


signal.signal(signal.SIGTERM, default_sigterm_handler)
