from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic.dataclasses import dataclass

from typing import Dict, List
from ..api.constants import JOB_ID, JOB_SOURCE_NAME, JOB_SOURCE_TYPE, JOB_STATUS, MODEL_ID, MODEL_NAME, PROJECT_LAYER_ITERATION_TYPE, PROJECT_LAYER_MODELS

@dataclass
class SieveModel:
    """
    Class for a model that exists within a Sieve workflow layer

    Fields:
        id:
            a unique ID given to a model by Sieve
        name:
            a name given to the model by a user
        version:
            a version number for a model
        status:
            the status of the model
    """
    id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None

    @property
    def dict(self) -> Dict:
        if self.id == None and self.name == None:
            raise Exception("SieveModel must have either an id or a name")
        if self.id != None and self.name != None:
            return {
                MODEL_ID: self.id,
                MODEL_NAME: self.name
            }
        if self.id != None:
            return {
                MODEL_ID: self.id
            }
        if self.name != None:
            return {
                MODEL_NAME: self.name
            }
    
    @classmethod
    def from_json(cls, model_json) -> SieveModel:
        return SieveModel(
            id=model_json.get(MODEL_ID, None),
            name=model_json.get(MODEL_NAME, None),
            version=model_json.get("version", None),
            status=model_json.get("status", None)
        )

class SieveLayerIterationType(Enum):
    video: str = 'video'
    objects: str = 'objects'

@dataclass
class SieveLayer:
    """
    Class for a Sieve workflow layer

    Fields:
        iteration_type:
            the system-given name for the user
        models:
            a list of models that run within a given layer
    """
    iteration_type: SieveLayerIterationType
    models: List[SieveModel]

    @property
    def dict(self) -> Dict:
        return {
            PROJECT_LAYER_ITERATION_TYPE: self.iteration_type.value,
            PROJECT_LAYER_MODELS: [model.dict for model in self.models]
        }
    
    @classmethod
    def from_json(cls, layer_json) -> SieveLayer:
        iteration_type = layer_json[PROJECT_LAYER_ITERATION_TYPE]
        models = [SieveModel.from_json(model_json) for model_json in layer_json[PROJECT_LAYER_MODELS]]
        return SieveLayer(
            iteration_type=iteration_type,
            models=models
        )


@dataclass
class SieveWorkflow:
    """
    Class for Sieve workflow configuration

    Fields:
        layers:
            a list of layers that make up a workflow

    """
    layers: List[SieveLayer]
    @classmethod
    def from_json(cls, workflow_json) -> SieveWorkflow:
        layers = [SieveLayer.from_json(layer_json) for layer_json in workflow_json]
        return SieveWorkflow(
            layers=layers
        )
