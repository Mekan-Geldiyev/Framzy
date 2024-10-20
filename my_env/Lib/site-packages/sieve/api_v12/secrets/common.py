import requests
import os

from sieve.api_v12.constants import API_URL, API_BASE
from ..utils import get_api_key
from pydantic import BaseModel
import base64
import pickle
import json

def get(name=None, API_KEY=None, limit = 10000, offset = 0):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/secrets/{name}", params={"limit": limit, "offset": offset}, headers=headers)
    rjson = r.json()
    return rjson

def list(limit=10000, offset=0, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/secrets", params={"limit": limit, "offset": offset}, headers=headers)
    rjson = r.json()
    return rjson["data"], rjson["next_offset"]

def create(name=None, value=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    data = {
        "value": value
    }
    sdata = json.dumps(data)
    r = requests.post(f"{API_URL}/{API_BASE}/secrets/{name}", headers=headers, data=sdata)
    return r.json()

def delete(name=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.delete(f"{API_URL}/{API_BASE}/secrets/{name}", headers=headers)
    return r.json()

def update(name=None, value=None, API_KEY=None):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    data = {
        "value": value
    }
    sdata = json.dumps(data)
    r = requests.put(f"{API_URL}/{API_BASE}/secrets/{name}", headers=headers, data=sdata)
    return r.json()

