"""
This module describes how we handle manual cost tracking in Sieve.
"""
global_handler = None


def get_global_handler():
    global global_handler
    if global_handler is None:
        global_handler = CostHandler()
    return global_handler


import threading


class CostHandler:
    """
    This class handles billing interaction for approved organizations in Sieve.

    It is responsible for tracking and updating the cost of a prediction as manually tracked
    by the function owner. It is useful for approved organizations to manually bill users
    at predict time.
    """

    def __init__(self):
        self._current_cost_dollars = 0
        self._lock = threading.Lock()

    def get_override_cost_dollars(self):
        with self._lock:
            return self._current_cost_dollars

    def set_override_cost_dollars(self, cost_dollars):
        with self._lock:
            self._current_cost_dollars = cost_dollars

    def add_override_cost_dollars(self, cost_dollars):
        with self._lock:
            self._current_cost_dollars += cost_dollars

    def reset_override_cost_dollars(self):
        with self._lock:
            current_cost_dollars = self._current_cost_dollars
            self._current_cost_dollars = 0
            return current_cost_dollars


def bill(cost_dollars):
    """
    This function is used to manually bill a user for a prediction.

    :param cost_dollars: The cost in dollars to bill the user
    :type cost_dollars: float
    """
    get_global_handler().add_override_cost_dollars(cost_dollars)


def view_bill():
    """
    This function is used to view the current cost of a prediction.

    :return: The current cost in dollars
    :rtype: float
    """
    return get_global_handler().get_override_cost_dollars()
