import requests
import os

from sieve.api_v12.constants import API_URL, API_BASE
from ..utils import get_api_key
from pydantic import BaseModel

class WorkflowReference(BaseModel):
    id: str
    name: str

    def info(self, API_KEY=None):
        return info(self.name, API_KEY=API_KEY)

    def delete(self, API_KEY=None):
        return delete(self.name, API_KEY=API_KEY)

def info(workflow_name=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/workflows/{workflow_name}", headers=headers)
    data = r.json()
    data['status'] = r.status_code
    return data

def delete(workflow_name=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.delete(f"{API_URL}/{API_BASE}/workflows/{workflow_name}", headers=headers)
    return r.json()

def list(limit=10000, offset=0, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/workflows", params={"limit": limit, "offset": offset}, headers=headers)
    rjson = r.json()
    return rjson["data"], rjson["next_offset"]

def search(mongo_filter_dict, limit=10000, offset=0, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.post(f"{API_URL}/{API_BASE}/workflows", params={"limit": limit, "offset": offset}, json=mongo_filter_dict, headers=headers)
    rjson = r.json()
    return rjson["data"], rjson["next_offset"]