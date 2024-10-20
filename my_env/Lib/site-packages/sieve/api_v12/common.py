from ..functions.function import _Function, Model
from typing import Any
from ..types.base import Struct
from sieve.api_v12.constants import API_URL, API_BASE
import importlib.util
import inspect
import uuid
import os
import requests
import json
import time
from ..functions.function import get_json_schema, get_input_names, get_output_names
from ..workflows.workflow import _Workflow
from networkx.readwrite import json_graph
from typing import Union, Dict
from ..functions.function import get_dict
from ..workflows.config import Workflow
from .utils import get_api_key
from .jobs.common import JobReference
from .models.common import ModelReference
from .workflows.common import WorkflowReference
from rich import print
import cloudpickle
import base64
import pickle
import shutil
from pathlib import Path

checkmark = ":white_check_mark:"
error_str = "[red bold]ERROR:[/red bold]"
success_str = "[green bold]SUCCESS:[/green bold]"

def upload(a: Any, version: str = None, API_KEY: str = None, single_build: bool = True):
    """
    Decorator to upload a function to the cloud.
    """
    api_key = get_api_key(API_KEY)

    _Function.upload = True
    if version is None:
        version = str(uuid.uuid4())
    model_name = a.name
    if isinstance(a, _Function):
        # print(f"Validating {a.name}...", end='', flush=True)
        # TODO: Upload function to cloud
        # validate_function(a)
        # print(checkmark)
        tmp_config = {}
        tmp_config["name"] = a.name
        tmp_config["gpu"] = str(a.gpu).lower()
        tmp_config["python_packages"] = a.python_packages
        tmp_config["system_packages"] = a.system_packages
        tmp_config["filepath"] = a.relative_path
        tmp_config["inputs"] = get_input_names(a)
        tmp_config["outputs"] = get_output_names(a)
        tmp_config["version"] = version
        tmp_config["python_version"] = a.python_version
        tmp_config["cuda_version"] = a.cuda_version
        tmp_config["system_version"] = a.system_version
        tmp_config["local_name"] = a.local_name
        tmp_config["is_iterator_input"] = a.is_iterator_input
        tmp_config["persist_output"] = a.persist_output
        tmp_config["is_iterator_output"] = inspect.isgeneratorfunction(a.function)
        tmp_config["machine_type"] = a.machine_type
        tmp_config["type"] = "function"
        tmp_config["run"] = a.run_commands
        tmp_config["env"] = a.env
        config = {}
        for a, val in tmp_config.items():
            if val is not None:
                config[a] = val
        print(f"Uploading function {model_name}...", end='', flush=True)
    else:
        tmp_config = {}
        tmp_config["name"] = a.name
        tmp_config["gpu"] = str(a.gpu).lower()
        tmp_config["python_packages"] = a.python_packages
        tmp_config["system_packages"] = a.system_packages
        tmp_config["filepath"] = a.relative_path
        tmp_config["inputs"] = get_input_names(a.function)
        tmp_config["outputs"] = get_output_names(a.function)
        tmp_config["version"] = version
        tmp_config["python_version"] = a.python_version
        tmp_config["cuda_version"] = a.cuda_version
        tmp_config["system_version"] = a.system_version
        tmp_config["local_name"] = a.local_name
        tmp_config["is_iterator_input"] = a.function.is_iterator_input
        tmp_config["persist_output"] = a.function.persist_output
        tmp_config["is_iterator_output"] = inspect.isgeneratorfunction(a.function.function)
        tmp_config["machine_type"] = a.machine_type
        tmp_config["type"] = "model"
        tmp_config["run"] = a.function.run_commands
        tmp_config["env"] = a.env

        config = {}
        for a, val in tmp_config.items():
            if val is not None:
                config[a] = val

        print(f"Uploading model {model_name}...", end='', flush=True)

    parent_path = str(Path(config["filepath"]).parents[0])
    zip_path = shutil.make_archive(f"{parent_path}", 'zip', parent_path)
    if not zip_path:
        print(f"\n{error_str} There was an issue zipping up {parent_path}")
        return

    upload_url_url = f'{API_URL}/{API_BASE}/upload_url'
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json',
    }
    payload = {"file_name": str(uuid.uuid4())}

    upload_response = requests.request("POST", upload_url_url, headers=headers, json=payload)

    upload_url_json = upload_response.json()
    upload_url = upload_url_json['upload_url']
    headers = {
        'x-goog-content-length-range': '0,10000000000'
    }
    file_upload_response = requests.request("PUT", upload_url, headers=headers, data=open(zip_path, 'rb'))

    url = f'{API_URL}/{API_BASE}/models/upload'
    payload = {"dir_url": upload_url_json['get_url'], "config": config}
    headers = {
        'X-API-KEY': api_key,
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    os.remove(zip_path)

    if 200 <= response.status_code < 300:
        model_id = response.json()["id"]

        # Get user info
        out = requests.get(f'{API_URL}/{API_BASE}/auth/user', headers=headers)
        if 200 <= out.status_code < 300:
            user_info = out.json()
            name = user_info['name']
            print(checkmark)
            print(f"Building {model_name} with id={model_id}...", end='', flush=True)
            _Function.upload = False

            model = ModelReference(id=model_id, name=model_name, version=version)
            curr_status = model.status()
            while curr_status != 'ready':
                if curr_status == 'error':
                    print(f"\n{error_str} There was an issue building your model. View logs with `sieve model logs {model_id}`")
                    return
                time.sleep(1)
                curr_status = model.status()

            print(checkmark + '\n')

            if single_build:
                print("Your model has been built. Your model id is " + model_id + f". Your model version is {version}. You can check the status of your model at https://sievedata.com/app/" + name + "/models")
            return model
        else:
            print(f"There was an issue retrieving your user info, but your model with id {model_id} should be processing:" + out.text)
        return ModelReference(id=model_id, name=model_name, version=version)
    if 400 <= response.status_code < 500:
        print(f"\n{error_str} There was an issue processing your model: {response.text}")
    if 500 <= response.status_code < 600:
        print(f"\n{error_str} There was an issue processing your model: {response.text}")
    # else:
    #     raise TypeError("Invalid argument to upload", a)
    _Function.upload = False

def deploy(workflow: _Workflow, API_KEY: str = None):
    """
    Decorator to deploy a workflow to the cloud.
    """
    api_key = get_api_key(API_KEY)

    if not issubclass(type(workflow), _Workflow):
        raise TypeError("Invalid argument to deploy", workflow)

    print(f"Deploying workflow {workflow.name}...", end='', flush=True)

    graph = workflow()
    graph_dict = json_graph.node_link_data(graph)
    wk = Workflow(config=graph_dict, name=workflow.name)
    data = wk.dict()
    url = f'{API_URL}/{API_BASE}/workflows/{workflow.name}'
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, json=data)
    if 200 <= response.status_code < 300:
        print(checkmark)
        return WorkflowReference(id=response.json()["id"], name=workflow.name)
    if response.status_code == 400:
        print(f"\nWorkflow already exists, attempting to edit...", end='', flush=True)
        url = f'{API_URL}/{API_BASE}/workflows/{workflow.name}'
        response = requests.request("PUT", url, headers=headers, json=data)
        if 200 <= response.status_code < 300:
            print(checkmark)
            return WorkflowReference(id=response.json()["id"], name=workflow.name)
        if 400 <= response.status_code < 500:
            print(f"\n{error_str} There was an issue editing your workflow: {response.text}")
    if 401 <= response.status_code < 600:
        print(f"\n{error_str} There was an issue processing your workflow: {response.text}")
    print()
    return

def delete(workflow: _Workflow, API_KEY: str = None):
    """
    Decorator to delete a workflow from the cloud.
    """

    if API_KEY is not None:
        api_key = API_KEY
    else:
        api_key = os.environ.get('SIEVE_API_KEY')
        if not api_key:
            print("Please set environment variable SIEVE_API_KEY with your API key")
            return

    if not issubclass(type(workflow), _Workflow):
        raise TypeError("Invalid argument to deploy", workflow)

    graph = workflow()
    graph_dict = json_graph.node_link_data(graph)
    wk = Workflow(config=graph_dict, name=workflow.name)
    data = wk.dict()
    url = f'{API_URL}/{API_BASE}/workflows/{workflow.name}'
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json',
    }
    response = requests.request("DELETE", url, headers=headers, json=data)
    if 200 <= response.status_code < 300:
        print("Your workflow has been deleted!")
    if 400 <= response.status_code < 500:
        print("There was an issue processing your workflow. " + response.text)
    if 500 <= response.status_code < 600:
        print("There was an issue processing your workflow. " + response.text)

def push(workflow: Union[_Workflow, str], inputs: Dict[str, Any], API_KEY: str = None, name: str = None, wait: bool = False, env: Dict[str, str] = {}):
    """
    Decorator to push inputs to a workflow currently in the cloud
    """
    api_key = get_api_key(API_KEY)

    if name is None:
        name = str(uuid.uuid4())

    if type(workflow) == str:
        workflow_name = workflow
    else:
        if not issubclass(type(workflow), _Workflow):
            raise TypeError("Invalid argument to push", workflow)
        workflow_name = workflow.name

    url = f'{API_URL}/{API_BASE}/push'

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json',
    }

    pickled_inputs = {}
    for key, value in inputs.items():
        pickled_inputs[key] = base64.b64encode(cloudpickle.dumps(value)).decode('ascii')

    data = {"workflow_name": workflow_name, "inputs": pickled_inputs, "env": env}

    response = requests.request("POST", url, headers=headers, json=data)
    if 200 <= response.status_code < 300:
        rjson = response.json()
        jid = rjson["id"]
        print(f"Pushed job with id={jid} {checkmark}")

        job_ref = JobReference(id=jid)
        if not wait:
            return job_ref
        curr_status = job_ref.status()
        while curr_status != 'finished': 
            if curr_status == 'error':
                print(f"\n{error_str} There was an issue with your job. Please run `sieve job get {jid}` to get detailed logs")
                return
            time.sleep(1)
            curr_status = job_ref.status()

        print(f"{success_str} Finished job successfully {checkmark}\n")
        return JobReference(id=jid)
    if 400 <= response.status_code < 500:
        print(f"\n{error_str}There was an issue processing your job: {response.text}")
    if 500 <= response.status_code < 600:
        print(f"\n{error_str}There was an issue processing your job: {response.text}")

def get(job_id=None, API_KEY=None, limit = 10000, offset = 0):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }

    # Get the pickled outputs for client
    r = requests.get(f"{API_URL}/{API_BASE}/jobs/{job_id}", params={"raw_data": 1, "limit": limit, "offset": offset}, headers=headers)
    rjson = r.json()

    obj_results = []
    for res in rjson['data']:
        unpickled_out = pickle.loads(base64.b64decode(res['output']))
        obj_results.append(unpickled_out)
    rjson['data'] = obj_results
    return rjson

def logs(job_id=None, model_id=None, workflow_id=None, id=None, API_KEY=None, limit = 100, offset = b''):
    api_key = get_api_key(API_KEY)
    headers = {
        "X-API-Key": api_key,
        'Content-Type': 'application/json',
    }
    r = requests.get(f"{API_URL}/{API_BASE}/logs", params={"job_id": job_id, "model_id": model_id, "workflow_id": workflow_id, "id": id, "limit": limit, "offset": offset}, headers=headers)
    rjson = r.json()
    return rjson