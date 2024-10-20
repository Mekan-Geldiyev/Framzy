# TODO: Deprecate and move to /v2/functions endpoints
from typing import Optional
import requests

from sieve.api.constants import API_URL, API_BASE
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from sieve.api.utils import get_api_key, sieve_request
from pydantic import BaseModel


class ModelReference(BaseModel):
    id: str
    name: str
    version: str
    owner: Optional[str]

    def info(self, API_KEY=None):
        return info(self.id, API_KEY=API_KEY)

    def status(self, API_KEY=None):
        return status(self.id, API_KEY=API_KEY)


def info(model_id=None, API_KEY=None):
    """
    Get a model by id
    """

    return sieve_request(
        "GET",
        f"models/{model_id}",
        api_key=API_KEY,
    )


def list(limit=10000, offset=0, API_KEY=None):
    """
    List all models
    """

    rjson = sieve_request(
        "GET",
        "models",
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
    )

    return rjson["data"], rjson["next_offset"]


def search(filter_dict, limit=10000, offset=0, API_KEY=None):
    """
    Search for models given a filter
    """
    rjson = sieve_request(
        "GET",
        "models",
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
    )

    return rjson["data"], rjson["next_offset"]


def status(job_id=None, API_KEY=None):
    """
    Check status of model deployment
    """
    return sieve_request(
        "GET",
        f"models/{job_id}/status",
        api_key=API_KEY,
    )
