import requests
from sieve.api.constants import API_URL, API_BASE
from sieve.api.utils import get_api_key, sieve_request
from pydantic import BaseModel


class WorkflowReference(BaseModel):
    id: str
    name: str

    def info(self, API_KEY=None):
        return info(self.name, API_KEY=API_KEY)

    def delete(self, API_KEY=None):
        return delete(self.name, API_KEY=API_KEY)


def info(workflow_name=None, API_KEY=None):
    return sieve_request(
        "GET",
        f"workflows/{workflow_name}",
        api_key=API_KEY,
    )


def delete(workflow_name=None, API_KEY=None):
    return sieve_request(
        "DELETE",
        f"workflows/{workflow_name}",
        api_key=API_KEY,
    )


def list(limit=10000, offset=0, API_KEY=None):
    rjson = sieve_request(
        "GET",
        "workflows",
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
    )

    return rjson["data"], rjson["next_offset"]


def search(mongo_filter_dict, limit=10000, offset=0, API_KEY=None):
    rjson = sieve_request(
        "POST",
        "workflows",
        json=mongo_filter_dict,
        params={"limit": limit, "offset": offset},
        api_key=API_KEY,
    )

    return rjson["data"], rjson["next_offset"]
