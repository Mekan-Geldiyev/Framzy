import requests
import os

from sieve.api_v12.constants import API_URL, API_BASE
from ..utils import get_api_key
from pydantic import BaseModel

class ModelReference(BaseModel):
    id: str
    name: str
    version: str

    def info(self, API_KEY=None):
        return info(self.id, API_KEY=API_KEY)
    
    def status(self, API_KEY=None):
        return status(self.id, API_KEY=API_KEY)


def info(job_id=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/models/{job_id}", headers=headers)
    return r.json()

def list(limit=10000, offset=0, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/models", params={"limit": limit, "offset": offset}, headers=headers)
    rjson = r.json()
    return rjson["data"], rjson["next_offset"]

def search(mongo_filter_dict, limit=10000, offset=0, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.post(f"{API_URL}/{API_BASE}/models", params={"limit": limit, "offset": offset}, json=mongo_filter_dict, headers=headers)
    rjson = r.json()
    return rjson["data"], rjson["next_offset"]

def status(job_id=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/models/{job_id}/status", headers=headers)
    return r.json()
    
