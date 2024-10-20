# FIXME version
import requests
import os

from sieve.api.constants import API_URL, API_BASE
from sieve.api.utils import get_api_key, sieve_request
from pydantic import BaseModel
import base64
import pickle


class JobReference(BaseModel):
    id: str

    def info(self, API_KEY=None):
        return info(self.id, API_KEY=API_KEY)

    def status(self, API_KEY=None):
        return status(self.id, API_KEY=API_KEY)


def get(job_id=None, API_KEY=None, limit=10000, offset=0):
    """
    Get a job by id
    """
    return sieve_request(
        "GET",
        f"jobs/{job_id}",
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
    )


def info(job_id=None, API_KEY=None):
    """
    Get information about a specific job
    """
    return sieve_request(
        "GET",
        f"jobs/{job_id}/info",
        api_key=API_KEY,
    )


def list(limit=10000, offset=0, API_KEY=None):
    """
    List all jobs
    """
    rjson = sieve_request(
        "GET",
        "jobs",
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
    )
    return rjson["data"], rjson["next_offset"]


def search(filter_dict, limit=10000, offset=0, API_KEY=None):
    """
    Search for jobs given a filter
    """
    rjson = sieve_request(
        "GET",
        "jobs",
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
        json=filter_dict,
    )
    return rjson["data"], rjson["next_offset"]


def status(job_id=None, API_KEY=None):
    """
    Get the status of a specific job
    """
    return sieve_request("GET", f"jobs/{job_id}/status", api_key=API_KEY)
