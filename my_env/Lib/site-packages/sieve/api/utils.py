"""
Utility functions for the Sieve API
"""

import json
from typing import Literal
from typing import Optional
import sys
import requests

import os

import os
import shutil
import zipfile
from requests.adapters import HTTPAdapter, Retry


from sieve import _openapi as openapi_client
from sieve._openapi.exceptions import ServiceException
from sieve.api.constants import API_BASE, API_URL, V2_API_BASE

from rich import print

IS_CLI = False


def parse_gitignore(gitignore_path):
    """Parse the .gitignore file and return a list of patterns to ignore."""

    ignore_patterns = []
    with open(gitignore_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ignore_patterns.append(line)
    return ignore_patterns


def zip_directory(directory_path, zip_filename):
    """Zip a directory and return the zip file path"""

    try:
        temp_directory = os.path.join(os.path.dirname(directory_path), "__temp__")

        # Remove files and directories mentioned in .gitignore
        sieveignore_path = os.path.join(directory_path, ".sieveignore")
        gitignore_path = os.path.join(directory_path, ".gitignore")
        ignore_patterns = [".git/*", ".git"]

        if os.path.exists(sieveignore_path):
            ignore_patterns.extend(parse_gitignore(sieveignore_path))
        else:
            if os.path.exists(gitignore_path):
                print(
                    "[yellow bold]Warning:[/yellow bold] using .gitignore is deprecated, please create a .sieveignore file\n"
                )
                ignore_patterns.extend(parse_gitignore(gitignore_path))

        shutil.copytree(
            directory_path,
            temp_directory,
            ignore=shutil.ignore_patterns(*ignore_patterns),
        )

        # Create the zip file
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_directory)
                    zipf.write(file_path, arcname)
    except BaseException as e:
        # Clean up the temporary directory and the zip file
        shutil.rmtree(temp_directory, ignore_errors=True)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        raise e

    # Clean up the temporary directory
    shutil.rmtree(temp_directory, ignore_errors=True)

    return zip_filename


def get_config_file_path():
    """
    Get the config file path
    """
    config_file_path = os.path.join(
        os.path.expanduser("~"), ".config", ".sieve", "config"
    )
    return config_file_path


def read_config_file():
    """
    Read the config file
    """
    path = get_config_file_path()
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return f.read()


def get_api_key(API_KEY=None):
    """Get the API key from the environment variable or from the argument"""
    if API_KEY is not None:
        api_key = API_KEY
    else:
        api_key = os.environ.get("SIEVE_API_KEY")
        if api_key is None:
            api_key = read_config_file()
        if not api_key:
            # Check if code is being run via CLI
            if IS_CLI:
                print("To get started with Sieve, please run: sieve login")
                print(
                    "Alternatively, populate the SIEVE_API_KEY environment variable with your API key. You can find your API key at https://www.sievedata.com/dashboard/settings"
                )
                sys.exit(1)
            else:
                raise ValueError(
                    "Please set environment variable SIEVE_API_KEY with your API key"
                )
    return api_key


def get_api_key_no_error(API_KEY=None):
    """Get the API key from the environment variable or from the argument"""
    if API_KEY is not None:
        api_key = API_KEY
    else:
        api_key = os.environ.get("SIEVE_API_KEY")
        if api_key is None:
            api_key = read_config_file()
    return api_key


def sieve_request(
    method,
    url,
    raise_on_status=True,
    parse_json=True,
    retry=True,
    api_key=None,
    api_version: Literal["v1", "v2"] = "v1",
    **kwargs,
) -> dict:
    """Make a request to the Sieve API"""

    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500])
    s.mount("https://", HTTPAdapter(max_retries=retries))

    r = (s if retry else requests).request(
        method=method,
        url=f"{API_URL}/{API_BASE if api_version == 'v1' else V2_API_BASE}/{url}",
        headers=(
            kwargs.get("headers")
            or {
                "X-API-KEY": api_key or get_api_key(),
                "Content-Type": "application/json",
            }
        ),
        **kwargs,
    )
    if raise_on_status:
        r.raise_for_status()

    if parse_json:
        try:
            return r.json()
        except requests.exceptions.JSONDecodeError:
            raise ValueError(
                f"Internal server error -- expected JSON output, received: {r.text}"
            )

    return r


class SieveApiError(Exception):
    def __init__(self, message, data=None):
        self.message = message
        self.data = data


class SieveApiClient(openapi_client.ApiClient):
    def response_deserialize(self, response_data, response_types_map):
        try:
            return super().response_deserialize(response_data, response_types_map)
        except ServiceException as e:
            data = json.loads(e.body)
            error_id = data.get("error_id", "<unknown>")

            raise SieveApiError(
                f"Sieve encountered an internal error! Please provide the following ID to support: {error_id}"
            ) from e
        except openapi_client.ApiException as e:
            message = e.body

            try:
                message = json.loads(e.body)["detail"]
            except:
                "Could not parse error message from API response."

            raise SieveApiError(f"{message} ({e.status})", data=message)


def make_api_client(
    api_url: Optional[str] = None, api_key: Optional[str] = None
) -> openapi_client.DefaultApi:
    key = api_key or get_api_key_no_error()
    api_conf = openapi_client.Configuration(
        host=api_url or os.environ.get("SIEVE_API_URL", "https://mango.sievedata.com"),
        api_key={"APIKeyHeader": key} if key else None,
    )
    return openapi_client.DefaultApi(SieveApiClient(api_conf))


ApiClient = make_api_client()
