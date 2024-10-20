import requests
import inspect
import functools
from typing import Union, Tuple

from sieve.api.utils import get_api_key

from ..types.base import Struct
import inspect
from typing import Dict, Any, List
import os
import networkx as nx
from .utils import type_to_str
from ..api.constants import API_URL, API_BASE
from .function import _Function, WrappedModelBase
from datetime import datetime
import uuid


class InvalidFunctionException(Exception):
    pass


class InvalidModelException(Exception):
    pass


class InvalidGraphException(Exception):
    pass


class InvalidTypeException(Exception):
    pass


def reference(name=None, id=None):
    """
    Reference a function or model.

    :param name: Name of the reference function or model
    :type name: str
    :param id: ID of the reference function or model
    :type id: str
    :return: Reference to the function or model
    :rtype: _Reference
    """

    return _Reference(name, id)


class _Reference:
    """This class is a reference to a function or model."""

    def __init__(self, name=None, id=None):
        """
        :param name: Name of the reference function or model
        :type name: str
        :param id: ID of the reference function or model
        :type id: str
        """

        self.id = id
        if name and "/" in name:
            self.author_name = name.split("/")[0]
            self.name = name.split("/")[1]
        else:
            self.name = name
            self.author_name = None
        if id is None and name is None:
            raise Exception(
                "You must provide either an id or a name to reference a function or model."
            )
        self._get_model_config()

    def _get_model_config(self):
        """
        Get the model config from the API. Loads it into reference.

        :raises Exception:
                - If the model is not found
                - If the API key is not set
        """

        if self.name is not None:
            if self.author_name is not None:
                url = (
                    API_URL
                    + "/"
                    + API_BASE
                    + "/models/"
                    + self.name
                    + f"?name=true&author_name={self.author_name}"
                )
            else:
                url = API_URL + "/" + API_BASE + "/models/" + self.name + "?name=true"
        else:
            url = API_URL + "/" + API_BASE + "/models/" + self.id
        headers = {
            "X-API-Key": get_api_key(None),
        }
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            if self.id is None:
                if self.author_name is not None:
                    raise Exception(
                        "Could not find model with name "
                        + self.name
                        + " as a publicly available model under user "
                        + self.author_name
                        + "."
                    )
                else:
                    raise Exception(
                        "Could not find model with name "
                        + self.name
                        + " under your account or as a publicly available model."
                    )
            else:
                raise Exception(
                    "Could not find model with id "
                    + self.id
                    + " under your account or as a publicly available model."
                )

        model_config_data = r.json()
        # TODO: Fix API and this
        if "data" in model_config_data:
            model_configs = model_config_data["data"]
            # Choose latest version
            latest_time = datetime(1970, 1, 1)
            for tmp_model_config in model_configs:
                # Format is like '2023-02-07T06:01:24.190+00:00'
                if "completed" not in tmp_model_config["time"]:
                    continue
                tmp_date = tmp_model_config["time"]["completed"]
                tmp_date = datetime.fromisoformat(tmp_date)
                if tmp_date > latest_time:
                    latest_time = tmp_date
                    model_config = tmp_model_config
        else:
            model_config = model_config_data
        self._inputs = model_config["inputs"]
        for i in self._inputs:
            if "type" not in i:
                continue
            if not i["type"]:
                del i["type"]
                continue

        self._outputs = model_config["outputs"]
        for i in self._outputs:
            if "type" not in i:
                continue
            if not i["type"]:
                del i["type"]
                continue

        self.type = model_config.get("type", "function")

        self.is_iterator_input = model_config.get("is_iterator_input", False)
        self.is_iterator_output = model_config.get("is_iterator_output", False)
        self.node_id = uuid.uuid4().hex
        if self.name is not None:
            self.id = model_config["id"]
        else:
            self.name = model_config["name"]

    def __call__(self, *args, **kwargs):
        """This function is called when the reference function or model is called. Doesn't do anything if not graphing."""

        if _Function.print_graph:
            return self._graph(*args, **kwargs)

        print("This doesn't do anything, it is a reference to a function or model.")

    def _has_input_name(self, name):
        """Helper function to check if the reference function or model has an input with the given name."""

        for inp in self._inputs:
            if inp["name"] == name:
                return True
        return False

    def _get_input_from_name(self, name):
        """Helper function to get the input with the given name."""

        for inp in self._inputs:
            if inp["name"] == name:
                return inp
        return None

    def _graph(self, *args, **kwargs):
        """
        This function is called when the reference function or model is called. It creates a graph from the reference and returns it.

        :return: NetworkX graph
        :rtype: nx.DiGraph
        """

        _Function.graph.add_node(
            self.node_id,
            name=self.name,
            type="function",
            inputs=get_input_names(self),
            outputs=get_output_names(self),
            is_iterator_input=self.is_iterator_input,
            is_iterator_output=self.is_iterator_output,
            model_id=self.id,
        )

        for name, (prev_node, param) in kwargs.items():
            if not self._has_input_name(name):
                raise InvalidGraphException(
                    f"Function {self.name} does not have an input named {name}."
                )

            if "type" in self._get_input_from_name(name):
                if param is not inspect._empty and type_to_str(
                    self._get_input_from_name(name)["type"]
                ) != type_to_str(param):
                    raise InvalidGraphException(
                        f"Function {self.name} has an input named {name} with type {self._get_input_from_name(name)['type']} but was passed an input with type {param}."
                    )

            _Function.graph.add_edge(prev_node, self.node_id, input=name)

        input_names = [inp["name"] for inp in self._inputs]
        for item in args:
            if issubclass(type(item), WrappedModelBase):
                # Ignore the surrounding model for model wrapped functions
                continue
            try:
                (prev_node, param) = item
            except:
                raise InvalidFunctionException(
                    f"Function {self.name} has been provided with an invalid input in the workflow {item}. Make sure you only pass in values directly from other functions or the inputs to the workflow."
                )
            try:
                input_name = input_names.pop(0)
            except:
                raise InvalidFunctionException(
                    f"Function {self.name} has been provided too many inputs in the workflow."
                )

            if "type" in self._get_input_from_name(input_name):
                if param is not inspect._empty and type_to_str(
                    self._get_input_from_name(input_name)["type"]
                ) != type_to_str(param):
                    raise InvalidGraphException(
                        f"Function {self.name} has an input named {input_name} with type {self._get_input_from_name(input_name)['type']} but was passed an input with type {param}."
                    )

            _Function.graph.add_edge(prev_node, self.node_id, input=input_name)

        out = (self.node_id, get_output_type(self))
        return out


def get_input_names(ref: _Reference):
    """Helper function to get the input names from the reference function or model."""

    inputs = []
    for i in ref._inputs:
        elem = {}
        elem["name"] = i["name"]
        if "type" in i:
            elem["type"] = i["type"]
        inputs.append(elem)
    return inputs


def get_output_names(ref: _Reference):
    """Helper function to get the output names from the reference function or model."""

    outputs = []
    for i in ref._outputs:
        elem = {}
        if "type" in i:
            elem["type"] = i["type"]
        outputs.append(elem)
    return outputs


def get_output_type(ref: _Reference):
    """Helper function to get the output type from the reference function or model."""
    return ref._outputs[0].get("type", inspect._empty)
