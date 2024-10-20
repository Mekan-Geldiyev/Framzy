import click
import os
import requests
from sieve.api.constants import API_URL, API_BASE
import uuid
from sieve.predictors.utils import load_config

from traitlets import default
@click.command()
@click.option('--command', default='download', help='commands using models')
@click.option('--model_version', default=None, help='retrain model')
def weights(command, model_version):
    if command == "download":
        download_command(model_version=model_version)

def download_command(API_KEY=None, model_version=None):
    model_config = load_config()
    model_name = model_config.get("model_name")
    weights_directory = model_config.get("weights_directory")
    if model_name is None:
        print("Please set model_name in your sieve.yaml file")
        return
    if weights_directory is None:
        print("Model has no weights directory in sieve.yaml file")
        return

    if API_KEY is not None:
        api_key = API_KEY
    else:
        api_key = os.environ.get('SIEVE_API_KEY')
        if not api_key:
            print("Please set environment variable SIEVE_API_KEY with your API key")
            return

    url = f'{API_URL}/{API_BASE}/get_weights_url'
    headers = {
        'X-API-KEY': api_key,
    }
    params = {
        "model_name": model_name,
        "model_version": model_version
    }

    response = requests.request("GET", url, headers=headers, params=params)

    if 200 <= response.status_code < 300:
        get_url = response.json().get("get_url")
        if get_url is None:
            print("There was an issue downloading your weights. " + response.text)
            return
        
        # Download the weights zip from the get_url
        weights_response = requests.request("GET", get_url)
        if 200 <= weights_response.status_code < 300:
            with open("weights.zip", "wb") as f:
                f.write(weights_response.content)
            # Unzip the weights in current directory
            if not os.path.exists(weights_directory):
                os.mkdir(weights_directory)
            os.system(f"unzip weights.zip -d {weights_directory}")
            os.remove("weights.zip")
            print("Your weights have been downloaded to the current directory")
        else:
            print("There was an issue downloading your weights. " + response.text)
        return

    if 400 <= response.status_code < 500:
        print(f"There was an issue downloading your weights with status code {response.status_code}" + response.text)
        return
        
    print("Response text: " + response.text)
    print("There was an internal error while processing your model. If this problem persists, please contact sieve support")