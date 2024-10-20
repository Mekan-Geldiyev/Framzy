"""
Auth related helper for Sieve API
"""

import os

SIEVE_API_KEY = os.environ.get("SIEVE_API_KEY", None)


def api_key():
    """Check if the API key is set."""

    if SIEVE_API_KEY is None:
        raise Exception(
            "SIEVE_API_KEY not set. Please set the environment variable SIEVE_API_KEY to your API key."
        )
    return SIEVE_API_KEY
