"""
Utility functions for the Sieve API
"""

import requests
from .auth import api_key
import os

def get_api_key(API_KEY):
    if API_KEY is not None:
        api_key = API_KEY
    else:
        api_key = os.environ.get('SIEVE_API_KEY')
        if not api_key:
            raise ValueError("Please set environment variable SIEVE_API_KEY with your API key")
    return api_key