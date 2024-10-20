from typing import ClassVar, Dict, List, Optional, Union, Any
from .base import SieveBaseModel
from .misc import Point, BoundingBox
from pydantic import validator, Extra, Field
import uuid
from .constants import *
from .object import Object, StaticObject, Temporal, SingleObject, Object

class Output(SieveBaseModel, extra=Extra.allow):
    """Base class for all outputs"""
    
    fields: ClassVar[Dict[str, type]] = {
    }

    defaults: ClassVar[Dict[str, Field]] = {
    }

    def to_object(self) -> Object:
        pass

    def from_object(obj: Object) -> 'Output':
        pass

class TemporalOutput(Output):
    """Base class for all temporal outputs"""
    
    fields: ClassVar[Dict[str, type]] = {
    }

    defaults: ClassVar[Dict[str, Field]] = {
    }

    def to_object(self) -> SingleObject:
        pass

    def from_object(obj: SingleObject) -> 'TemporalOutput':
        pass


class StaticOutput(Output):
    """Base class for all temporal outputs"""
    
    fields: ClassVar[Dict[str, type]] = {
    }

    defaults: ClassVar[Dict[str, Field]] = {
    }

    def to_object(self) -> StaticObject:
        pass

    def from_object(obj: StaticObject) -> 'TemporalOutput':
        pass

class Detection(TemporalOutput):
    """
    A detection is a way of representing something that you have detected in a frame, and transforming it into an object.
    """

    fields: ClassVar[Dict[str, type]] = {
        OBJECT_ID: str,
        BOUNDING_BOX: BoundingBox,
        SCORE: float,
        FRAME_NUMBER: int,
        CLASS: str,
    }

    defaults: ClassVar[Dict[str, Field]] = {
        OBJECT_ID: None,
        CLASS: "unknown",
        SCORE: 1.0
    }

    def to_object(self) -> SingleObject:
        temporal_dict = {
            FRAME_NUMBER: self.get_attribute(FRAME_NUMBER),
            BOUNDING_BOX: self.get_attribute(BOUNDING_BOX),
            SCORE: self.get_attribute(SCORE),
        }
        # Iterate through attrs and add them to the temporal dict
        for attr in self.__fields__.keys():
            if attr not in [OBJECT_ID, CLASS, FRAME_NUMBER, BOUNDING_BOX, SCORE]:
                temporal_dict[attr] = self.get_attribute(attr)

        temporal = Temporal(**temporal_dict)
        object_dict = {
            OBJECT_ID: self.get_attribute(OBJECT_ID),
            CLASS: self.get_attribute(CLASS),
            TEMPORAL: [temporal]
        }
        return SingleObject(**object_dict)

    def from_object(obj: Object) -> 'Detection':
        temporal = obj.get_attribute(TEMPORAL)[-1]
        detection_dict = {
            OBJECT_ID: obj.get_attribute(OBJECT_ID),
            CLASS: obj.get_attribute(CLASS),
            FRAME_NUMBER: temporal.get_attribute(FRAME_NUMBER),
            BOUNDING_BOX: temporal.get_attribute(BOUNDING_BOX),
            SCORE: temporal.get_attribute(SCORE, 1),
        }
        return Detection(**detection_dict)

class TemporalClassification(TemporalOutput):

    """
    A temporal classification is a way of attaching a immediately detected temporal attribute to an object.
    """

    fields: ClassVar[Dict[str, type]] = {
        OBJECT: Object,
    }

    def to_object(self) -> Object:
        object_dict = self.get_attribute(OBJECT).dict()
        
        #Get all attributes other than OBJECT
        other_attributes = {k: v for k, v in self.dict().items() if k != OBJECT}

        #Add other attributes to the object
        last_temporal: Temporal = object_dict.get(TEMPORAL)[-1]
        last_temporal.update(other_attributes)

        return Object(**object_dict)

    def from_object(obj: Object) -> 'TemporalClassification':
        temporal_dict = obj.get_attribute(TEMPORAL)[-1].dict()
        temporal_dict[OBJECT] = obj
        return TemporalClassification(**temporal_dict)

class StaticClassification(StaticOutput):

    """
    A static classification is a way of attaching a static attribute to an object.
    """

    fields: ClassVar[Dict[str, Field]] = {
        OBJECT: Object,
    }

    def to_object(self) -> StaticObject:
        object_dict = self.get_attribute(OBJECT).dict()

        #Delete temporal attribute
        if TEMPORAL in object_dict:
            del object_dict[TEMPORAL]
        
        #Get all attributes other than OBJECT
        other_attributes = {k: v for k, v in self.dict().items() if k != OBJECT}

        #Add other attributes to the object
        object_dict.update(other_attributes)

        return StaticObject(**object_dict)

    def from_object(obj: Object) -> 'StaticClassification':
        object_dict = obj.dict()
        object_dict[OBJECT] = obj
        return StaticClassification(**object_dict)