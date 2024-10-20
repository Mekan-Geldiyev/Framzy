import requests
from sieve import _openapi
from sieve.api.utils import ApiClient, get_api_key, sieve_request
from sieve.api.constants import API_URL, API_BASE
import json


def get(name: str) -> _openapi.Secret:
    """
    Get a secret by name
    """
    return ApiClient.get_secret(name)


def list(limit=10000, offset=0) -> _openapi.ListResponseSecret:
    """
    List all secrets
    """

    return ApiClient.list_secrets(limit=limit, offset=offset)


def create(name: str, value=None):
    """Create a secret"""
    ApiClient.create_secret(name=name, body={"value": value})


def delete(name: str, API_KEY=None):
    """
    Delete a secret
    """
    ApiClient.delete_secret(name=name)


def update(name=None, value=None, API_KEY=None):
    """
    Update a secret
    """

    data = {"value": value}
    sdata = json.dumps(data)
    return sieve_request(
        "PUT",
        f"secrets/{name}",
        data=sdata,
        api_key=API_KEY,
    )
