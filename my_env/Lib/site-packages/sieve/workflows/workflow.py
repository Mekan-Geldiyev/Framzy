"""
This module contains the decorator to create a workflow
"""

import sieve
from ..functions.function import _Function
import inspect
import networkx as nx
import os
from ..functions.utils import type_to_str, type_to_schema
import docstring_parser
from ..types.metadata import Metadata


class InvalidWorkflowException(Exception):
    pass


class InvalidWorkflowException(Exception):
    pass


class _Workflow:
    def __init__(
        self,
        workflow,
        name,
        fps=5,
        output_keys=None,
        metadata: Metadata = None,
        **kwargs,
    ):
        """
        This class is a wrapper around the workflow function to create a workflow

        :param workflow: Workflow function
        :type workflow: function
        :param name: Name of the workflow
        :type name: str
        :param fps: Frames per second for the workflow
        :type fps: int
        :param output_keys: Output keys for the workflow
        :type output_keys: list
        :param metadata: Metadata for the workflow
        :type metadata: sieve.Metadata
        :param kwargs: Keyword arguments for the workflow
        :type kwargs: dict
        """
        self.workflow = workflow
        self.name = name
        self.fps = fps
        self.kwargs = kwargs
        self.output_keys = output_keys
        self.docstring = None
        self.param_descriptions = {}
        self.metadata = metadata
        if self.workflow.__doc__:
            self.docstring = docstring_parser.parse(self.workflow.__doc__)
            params = self.docstring.params
            for param in params:
                self.param_descriptions[param.arg_name] = param.description

    def __call__(self, *args, **kwargs):
        """
        This function is called when the workflow is called. It creates a graph and returns it.

        :return: NetworkX graph
        :rtype: nx.DiGraph
        """

        _Function.print_graph = True
        signature = inspect.signature(self.workflow)
        # Get all the input arg names and types
        input_args = {}
        _Function.graph = nx.DiGraph()
        for name, parameter in signature.parameters.items():
            inp = {"name": name}
            if parameter.annotation is not inspect._empty:
                inp["type"] = type_to_str(parameter.annotation)
                inp["schema"] = type_to_schema(parameter.annotation)
            if name in self.param_descriptions:
                inp["description"] = self.param_descriptions[name]
            input_args[name] = (name, parameter.annotation)
            _Function.graph.add_node(
                name,
                name=name,
                type="input",
                inputs=[],
                outputs=[inp],
                is_iterator_input=False,
                is_iterator_output=False,
            )

        # Check if number of args and kwargs > 0
        if len(input_args) == 0:
            raise InvalidWorkflowException(
                f"Workflow {self.name} must have at least one input"
            )

        out = self.workflow(**input_args)
        if len(out) == 0:
            raise Exception("Workflow must return at least one output")

        # Check if there are only inputs in the bucket
        if len(_Function.graph.nodes) == len(input_args):
            raise InvalidWorkflowException(
                f"Workflow {self.name} must have at least one function"
            )

        output_description = None
        if self.docstring and self.docstring.returns:
            output_description = self.docstring.returns.description
        if type(out[0]) is tuple or type(out[0]) is list:
            inputs = []
            for i, o in enumerate(out):
                prev_node, out_type = o
                if out_type is inspect._empty:
                    out_type = None
                _Function.graph.add_edge(
                    prev_node,
                    "output",
                    input=(
                        f"output:{i}"
                        if self.output_keys is None
                        else self.output_keys[i]
                    ),
                )
                inputs.append(
                    {
                        "name": f"output:{i}"
                        if self.output_keys is None
                        else self.output_keys[i],
                        "type": type_to_str(out_type),
                        "description": output_description,
                    }
                )
            _Function.graph.add_node(
                "output",
                name="output",
                type="output",
                inputs=inputs,
                outputs=[],
                is_iterator_input=False,
                is_iterator_output=False,
            )
        else:
            prev_node, _ = out
            out_type = signature.return_annotation
            if out_type is inspect._empty:
                out_type = None

            _Function.graph.add_edge(
                prev_node,
                "output",
                input="output:0" if self.output_keys is None else self.output_keys[0],
            )
            _Function.graph.add_node(
                "output",
                name="output",
                type="output",
                inputs=[
                    {
                        "name": "output:0"
                        if self.output_keys is None
                        else self.output_keys[0],
                        "type": type_to_str(out_type),
                        "description": output_description,
                    }
                ],
                outputs=[],
                is_iterator_input=False,
                is_iterator_output=False,
            )

        _Function.print_graph = False

        # Check if all inputs are connected in graph
        for node in _Function.graph.nodes:
            if (
                _Function.graph.nodes[node]["type"] == "input"
                and len(_Function.graph.out_edges(node)) == 0
            ):
                raise InvalidWorkflowException(
                    f"Input {node} is not connected to any function"
                )

        return _Function.graph


def workflow(workflow=None, *, name=None, fps=5, metadata: Metadata = None, **kwargs):
    """Decorator to create a workflow."""

    if workflow:
        return _Workflow(workflow, metadata=metadata)
    else:

        def wrapper(workflow):
            return _Workflow(workflow, name, fps, metadata=metadata, **kwargs)

        return wrapper
