from requests.adapters import HTTPAdapter
import sys
from sieve.api.utils import SieveApiError
from sieve._openapi.models.body_get_upload_url_v1_upload_url_post import (
    BodyGetUploadUrlV1UploadUrlPost,
)
from sieve._openapi.models.input_output import InputOutput
from sieve._openapi.models.organization_model import OrganizationModel
from sieve._openapi.models.push_request import PushRequest

from sieve._openapi.models.upload_model import UploadModel
from sieve._openapi.exceptions import ApiException

from sieve._openapi.models.user_model import UserModel
from sieve.types.metadata import Metadata
from sieve.api.utils import ApiClient
from sieve import _openapi
from ..functions.function import _Function, gpu
from typing import Any, Optional, Tuple
from sieve.api.constants import API_URL, API_BASE, V2_API_BASE
import inspect
import uuid
import os
import requests
import json
import time
from ..functions.function import get_input_names, get_output_names
from networkx.readwrite import json_graph
from typing import Union, Dict
from .utils import (
    get_config_file_path,
    make_api_client,
    sieve_request,
    zip_directory,
)
from sieve.api.utils import get_api_key
from .models.common import ModelReference
from rich import print
from rich.spinner import Spinner
from rich.live import Live
from rich.console import Console
import cloudpickle
import base64
import pickle
from pathlib import Path
from sseclient import SSEClient
import threading
from datetime import datetime


checkmark = ":white_check_mark:"
error_str = "[red bold]ERROR:[/red bold]"
success_str = "[green bold]SUCCESS:[/green bold]"
console = Console()


class BuildLogsThread(threading.Thread):
    def __init__(self, api_key, model_id, spinner):
        super().__init__()
        self.api_key = api_key
        self.model_id = model_id
        self.stop_flag = False
        self.spinner = spinner
        self.offset = int(datetime.now().timestamp() * 1e9)

    def run(self):
        start_streaming = False
        start_message = "pip install -r /tmp/requirements.txt"
        push_message = "The push refers to repository"
        pushing_image = False

        while not self.stop_flag:
            try:
                logs = sieve_request(
                    "GET",
                    f"logs?model_id={self.model_id}&stage=build&start_time={self.offset}",
                    api_key=self.api_key,
                    api_version="v2",
                )
            except requests.HTTPError:
                time.sleep(2)
                continue

            data = logs["data"]
            last_time = self.offset
            for msg in data:
                for log in msg["logs"]:
                    last_time = int(log["timestamp"]) + 1
                    log_lines = log["message"].split("\n")
                    for line in log_lines:
                        if start_message in line.strip():
                            start_streaming = True
                        if push_message in line.strip():
                            self.spinner.update(text=f"Pushing image...")
                            pushing_image = True
                            continue

                        if (
                            line.strip() == ""
                            or line == "\n"
                            or not start_streaming
                            or pushing_image
                        ):
                            continue
                        console.print("[yellow]" + line + "[/yellow]", highlight=False)
                        time.sleep(0.01)

            self.offset = last_time
            time.sleep(2)

    def stop(self):
        self.stop_flag = True


def upload(a: Any, version: str = None, API_KEY: str = None, single_build: bool = True):
    """
    Decorator to upload a Sieve model or function to the cloud.

    :param a: Model or function to upload
    :type a: Any
    :param version: Version of the model or function to upload
    :type version: str
    :param API_KEY: API key to use for authentication
    :type API_KEY: str
    :param single_build: If true, print a link to the model after building
    :type single_build: bool
    """
    api_key = get_api_key(API_KEY)

    _Function.upload = True
    if version is None:
        version = str(uuid.uuid4())
    model_name = a.name

    spin = Spinner("dots", text=f"Uploading {model_name}...")
    live = Live(spin, refresh_per_second=10, console=console)
    live.start()

    if isinstance(a, _Function):
        tmp_config = {}
        tmp_config["name"] = a.name
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
        tmp_config["type"] = "function"
        tmp_config["run"] = a.run_commands
        tmp_config["env"] = get_env_list_dict(a.environment_variables)
        tmp_config["public_data"] = process_metadata(a.metadata, api_key)
        tmp_config["restart_on_error"] = a.restart_on_error
        if a.machine_type and isinstance(a.machine_type, str):
            tmp_config["machine_type"] = a.machine_type
            tmp_config["gpu"] = str(
                a.machine_type != "cpu" and a.machine_type != "cpu-ondemand"
            ).lower()
            tmp_config["split"] = 1
        elif a.machine_type and isinstance(a.machine_type, gpu):
            gpu_type = a.machine_type.gpu if a.machine_type.gpu is not None else "cpu"
            tmp_config["machine_type"] = gpu_type
            tmp_config["gpu"] = str(gpu_type != "cpu").lower()
            tmp_config["split"] = a.machine_type.split
        elif a.gpu and isinstance(a.gpu, gpu):
            gpu_type = a.gpu.gpu if a.gpu.gpu is not None else "cpu"
            tmp_config["machine_type"] = gpu_type
            tmp_config["gpu"] = str(
                gpu_type != "cpu" and gpu_type != "cpu-ondemand"
            ).lower()
            tmp_config["split"] = a.gpu.split
        elif isinstance(a.gpu, bool):
            tmp_config["machine_type"] = "T4" if a.gpu else "cpu"
            tmp_config["gpu"] = str(a.gpu).lower()
            tmp_config["split"] = 1
        else:
            tmp_config["machine_type"] = a.gpu
            tmp_config["gpu"] = str(a.gpu != "cpu" and a.gpu != "cpu-ondemand").lower()
            tmp_config["split"] = 1
        config = {}
        for a, val in tmp_config.items():
            if val is not None:
                config[a] = val

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
        tmp_config["is_iterator_output"] = inspect.isgeneratorfunction(
            a.function.function
        )
        tmp_config["type"] = "model"
        tmp_config["run"] = a.function.run_commands
        tmp_config["env"] = get_env_list_dict(a.environment_variables)
        tmp_config["public_data"] = process_metadata(a.metadata, api_key)
        tmp_config["restart_on_error"] = a.restart_on_error
        if a.machine_type and isinstance(a.machine_type, str):
            tmp_config["machine_type"] = a.machine_type
            tmp_config["gpu"] = str(
                a.machine_type != "cpu" and a.machine_type != "cpu-ondemand"
            ).lower()
            tmp_config["split"] = 1
        elif a.machine_type and isinstance(a.machine_type, gpu):
            gpu_type = a.machine_type.gpu if a.machine_type.gpu is not None else "cpu"
            tmp_config["machine_type"] = gpu_type
            tmp_config["gpu"] = str(gpu_type != "cpu").lower()
            tmp_config["split"] = a.machine_type.split
        elif a.gpu and isinstance(a.gpu, gpu):
            gpu_type = a.gpu.gpu if a.gpu.gpu is not None else "cpu"
            tmp_config["machine_type"] = gpu_type
            tmp_config["gpu"] = str(
                gpu_type != "cpu" and gpu_type != "cpu-ondemand"
            ).lower()
            tmp_config["split"] = a.gpu.split
        elif isinstance(a.gpu, bool):
            tmp_config["machine_type"] = "T4" if a.gpu else "cpu"
            tmp_config["gpu"] = str(a.gpu).lower()
            tmp_config["split"] = 1
        else:
            tmp_config["machine_type"] = a.gpu
            tmp_config["gpu"] = str(a.gpu != "cpu" and a.gpu != "cpu-ondemand").lower()
            tmp_config["split"] = 1
        config = {}
        for a, val in tmp_config.items():
            if val is not None:
                config[a] = val

    parent_path = str(Path(config["filepath"]).parents[0])
    zip_path = os.path.join(parent_path, "archive.zip")
    try:
        zip_directory(parent_path, zip_path)
        resp = make_api_client(api_key=api_key).get_upload_url(
            BodyGetUploadUrlV1UploadUrlPost(file_name=str(uuid.uuid4()))
        )

        upload_url = resp.upload_url
        headers = {"x-goog-content-length-range": "0,10000000000"}
        requests.request("PUT", upload_url, headers=headers, data=open(zip_path, "rb"))

        try:
            response = make_api_client(api_key=api_key).upload_model(
                UploadModel(
                    dir_url=resp.get_url,
                    # FIXME: We should pass these in properly instead of using `from_dict`
                    config=_openapi.ConfigModel.from_dict(config),
                )
            )
        except SieveApiError as e:
            print(
                f"\n{error_str} There was an issue processing model '{model_name}'. {e.data}"
            )
            sys.exit(1)

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    model_id = response.id
    thread = BuildLogsThread(api_key, model_id, spin)
    thread.daemon = True
    thread.start()

    try:
        user_info = make_api_client(api_key=api_key).get_organization()
    except ApiException as e:
        print(
            f"There was an issue retrieving your user info, but your model with id {model_id} should be processing:"
            + (e.body or "<no data>")
        )
        return ModelReference(id=model_id, name=model_name, version=version, owner=None)

    name = user_info.name
    spin.update(text=f"Building {model_name}...")
    _Function.upload = False

    model = ModelReference(id=model_id, name=model_name, version=version, owner=name)
    curr_status = model.status(API_KEY=api_key)
    while curr_status != "ready":
        if curr_status == "error":
            print(
                f"\n{error_str} There was an issue building your model. View logs with `https://www.sievedata.com/functions/{name}/{model_name}/versions/{model_id}/build`"
            )
            return
        time.sleep(1)
        curr_status = model.status(API_KEY=api_key)

    thread.stop()
    live.update(f"[green]:heavy_check_mark:[/green] Deployed {model_name}\n")
    live.stop()

    if single_build:
        print(
            "Your model has been built. Your model id is "
            + model_id
            + f". Your model version is {version}. You can check the status of your model at https://sievedata.com/app/"
            + name
            + "/models"
        )
    return model


def get(job_id=None, API_KEY=None, limit=10000, offset=0):
    """
    Query jobs from the API

    :param job_id: Job id to query logs for
    :type job_id: str
    :param API_KEY: API key to use for authentication
    :type API_KEY: str
    :param limit: Number of logs to return
    :type limit: int
    :param offset: Offset to start from
    :type offset: int
    :return: Jobs
    :rtype: dict
    """

    rjson = sieve_request(
        "GET",
        f"jobs/{job_id}",
        api_key=API_KEY,
        params={"raw_data": 1, "limit": limit, "offset": offset},
    )

    obj_results = []
    for res in rjson["data"]:
        unpickled_out = pickle.loads(base64.b64decode(res["output"]))
        obj_results.append(unpickled_out)
    rjson["data"] = obj_results
    return rjson


def logs(
    job_id=None,
    model_id=None,
    workflow_id=None,
    id=None,
    API_KEY=None,
    limit=100,
    offset=b"",
):
    """
    Query logs from the API

    :param job_id: Job id to query logs for
    :type job_id: str
    :param model_id: Model id to query logs for
    :type model_id: str
    :param workflow_id: Workflow id to query logs for
    :type workflow_id: str
    :param id: id to query logs for in case of a single log
    :type id: str
    :param API_KEY: API key to use for authentication
    :type API_KEY: str
    :param limit: Number of logs to return
    :type limit: int
    :param offset: Offset to start from
    :type offset: bytes
    :return: Logs
    :rtype: dict
    """

    return sieve_request(
        "GET",
        "logs",
        api_key=API_KEY,
        params={
            "job_id": job_id,
            "model_id": model_id,
            "workflow_id": workflow_id,
            "id": id,
            "limit": limit,
            "offset": offset,
        },
    )


def upload_file(
    api_key: str, file_name: str, public_upload: bool, public_request: bool, file
):
    """
    Upload file to GCS and return authenticated (or public) URL
    :param api_key: API key to use for authentication
    :type api_key: str
    :param file_name: Name of file to upload (optional)
    :type file_name: str
    :param public_upload: Whether to upload the file publicly
    :type public_upload: bool
    :param public_request: Whether this is a public request (no auth). Used for public demos.
    :type public_request: bool
    :param file: File to upload
    :type file: file
    """

    response = ApiClient.get_upload_url(
        BodyGetUploadUrlV1UploadUrlPost(
            file_name=file_name or f"{uuid.uuid4()}",
            public_upload=public_request,
            public=public_upload,
        )
    )

    upload_headers = {
        "x-goog-content-length-range": "0,10000000000",
    }

    requests.put(response.upload_url, data=file, headers=upload_headers)
    file.close()
    return response.get_url


def process_metadata(metadata: Metadata, api_key: str):
    """
    Upload public data to cloud storage if needed and return public data struct
    :param metadata: Metadata to process
    :type metadata: Metadata
    :param api_key: API key to use for authentication
    :type api_key: str
    """
    if metadata is None:
        return {}

    public_data = metadata.dict()

    if metadata.image is not None:
        public_data["image"] = upload_file(
            api_key,
            file_name=None,
            public_upload=True,
            public_request=False,
            file=open(metadata.image.path, "rb"),
        )
    return public_data


def get_env_list_dict(env_list):
    """Get a list of env vars as a dict"""
    try:
        return [i.dict() for i in env_list]
    except:
        raise TypeError(
            "Badly supplied env vars, make sure you supply a list of sieve.Env config variables",
            env_list,
        )


def whoami(api_key: Optional[str] = None) -> Tuple[UserModel, OrganizationModel]:
    # Whoami is also used to test if the API key is valid
    client = make_api_client(api_key=api_key)
    return client.get_user_info(), client.get_organization()


def write_key(key: str):
    """
    This function writes the api key to the config file.
    """
    path = get_config_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(key)
