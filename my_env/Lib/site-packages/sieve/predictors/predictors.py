from ..types.frame import FrameFetcher, FrameObject, FrameSingleObject, FrameObjectSlice
from ..types.misc import  UserMetadata, SieveBaseModel
from ..types.object import Object, ObjectSlice, SingleObject, StaticObject
from ..types.outputs import Output, StaticOutput, TemporalOutput
from cog.predictor import BasePredictor
from typing import List, Union

# Added in Python 3.8. Can be from typing if we drop support for <3.8.

class SievePredictor(BasePredictor):
    """
    A SievePredictor is a predictor that can be used with the Sieve framework
    """
    ALLOWED_INPUT_TYPES = []
    ALLOWED_OUTPUT_TYPES = []
    artifacts_directory = None

    def get_artifacts_directory(self):
        return self.artifacts_directory

class TemporalPredictor(SievePredictor):
    """
    A temporal processor is a predictor that processes a objects with a temporal component over the last n frames
    """
    ALLOWED_INPUT_TYPES = [
        FrameObjectSlice,
        UserMetadata, 
        List[ObjectSlice],
        List[SingleObject],
        FrameSingleObject,
        FrameFetcher
    ]

    ALLOWED_OUTPUT_TYPES = [
        List[SingleObject],
        SingleObject,
        FrameSingleObject,
        TemporalOutput
    ]

class ObjectPredictor(SievePredictor):
    """
    An object processor is a predictor that processes a single object
    """
    ALLOWED_INPUT_TYPES = [
        FrameObjectSlice,
        Object,
        UserMetadata,
        FrameFetcher
    ]

    ALLOWED_OUTPUT_TYPES = [
        Object,
        StaticObject,
        ObjectSlice,
        SingleObject,
        StaticOutput
    ]

class LinearPredictor(SievePredictor):
    ALLOWED_INPUT_TYPES = [
        FrameObjectSlice,
        UserMetadata, 
        List[ObjectSlice],
        List[SingleObject],
        FrameSingleObject
    ]

    ALLOWED_OUTPUT_TYPES = [
        List[SingleObject],
        SingleObject
    ]

