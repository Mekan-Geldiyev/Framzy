"""
This module contains the Pydantic representation of configs for workflows
"""

from pydantic import BaseModel, Extra, Field
from typing import Union, Optional, Any, List, Dict


class ObjectSchema(BaseModel, extra=Extra.ignore):
    """
    Pydantic Representation of Input with NetworkX Config
    """

    name: Optional[str]
    type: Optional[str]
    description: Optional[str]
    schema_alias: Optional[Dict] = Field(alias="schema")


class Node(BaseModel, extra=Extra.ignore):
    """
    Pydantic Representation of Node with NetworkX Config
    """

    id: str
    name: Optional[str]
    type: str
    is_iterator_input: bool
    is_iterator_output: bool
    inputs: List[ObjectSchema]
    outputs: List[ObjectSchema]
    model_id: Optional[str]
    organization_id: Optional[str]


class Link(BaseModel, extra=Extra.ignore):
    """
    Pydantic Representation of Link with NetworkX Config
    """

    source: str
    target: str
    input: str


class WorkflowConfig(BaseModel, extra=Extra.ignore):
    """
    Pydantic Representation of Workflow Config with NetworkX Config
    """

    nodes: List[Node]
    links: List[Link]


class Workflow(BaseModel):
    """
    Pydantic Representation of the Workflow with NetworkX Config
    """

    name: str
    config: WorkflowConfig
