from typing import ClassVar, Dict, List, Optional, Union, Any
from .base import SieveBaseModel
from .misc import Point, BoundingBox
from pydantic import validator, Extra, Field
from .constants import *

class Temporal(SieveBaseModel, extra=Extra.allow):
    """
    A temporal object contains all temporal/state information about an object that may change over time.
    This includes, at minimum, the object's bounding box and its velocity
    """

    fields: ClassVar[Dict[str, type]] = {
        BOUNDING_BOX: BoundingBox,
        VELOCITY: Point,
        FRAME_NUMBER: int
    }

    defaults: ClassVar[Dict[str, Field]] = {
        VELOCITY: Point(x=0, y=0)
    }

    def center(self) -> Point:
        bounding_box: BoundingBox = self.get_attribute(BOUNDING_BOX)
        return Point(x=(bounding_box.x1 + bounding_box.x2) / 2, y=(bounding_box.y1 + bounding_box.y2) / 2)

class StaticObject(SieveBaseModel, extra=Extra.allow):
    """
    A static object contains all static information about an object that does not change over time.
    This includes, at minimum, the object's class and its attributes
    """

    fields: ClassVar[Dict[str, type]] = {
        OBJECT_ID: str,
        CLASS: str,
        START_FRAME: int,
        END_FRAME: int,
        SKIP_FRAMES: int
    }

    defaults: ClassVar[Dict[str, Field]] = {
        OBJECT_ID: None,
        SKIP_FRAMES: 1
    }
        
    def __init__(self, **data) -> None:
        if END_FRAME not in data and START_FRAME in data:
            data[END_FRAME] = data[START_FRAME]
        elif END_FRAME not in data and START_FRAME not in data and FRAME_NUMBER in data:
            data[START_FRAME] = data[FRAME_NUMBER]
            data[END_FRAME] = data[FRAME_NUMBER]
        elif END_FRAME not in data and START_FRAME not in data and FRAME_NUMBER not in data:
            raise ValueError("must have either start_frame or frame_number")
        if data[END_FRAME] < data[START_FRAME]:
            raise ValueError("End frame must be greater than start frame")
        if "class" in data:
            data[CLASS] = data["class"]
            del data["class"]
        super().__init__(**data)

    @validator(START_FRAME, END_FRAME, check_fields=False)
    def check_valid(cls, v):
        """
        Check that the start and end frames are valid
        """
        if type(v) != int:
            raise ValueError("must be int")
        return v

class Object(StaticObject, extra=Extra.allow):
    """
    Am object contains all information about an object that is tracked over time.
    This includes, at minimum, the object's bounding box and its velocity.
    It also contains all static information about the object, such as its class and object id
    """

    #Combine fields with the fields of the parent classes
    fields : ClassVar[Dict[str, type]] = {
        TEMPORAL: List[Temporal]
    }

    defaults: ClassVar[Dict[str, Field]] = {
        TEMPORAL: []
    }

    # init with kwargs
    def __init__(self, **data):
        if type(data[TEMPORAL]) != list:
            data[TEMPORAL] = [data[TEMPORAL]]
        for i, val in enumerate(data[TEMPORAL]):
            if type(val) != Temporal and type(val) == dict:
                data[TEMPORAL][i] = Temporal(**val)
            elif not issubclass(type(val), Temporal):
                raise TypeError("Temporal must be of type Temporal or dict to be converted to Temporal")
        if TEMPORAL in data and type(data[TEMPORAL]) == list and len(data[TEMPORAL]) > 0 and END_FRAME not in data and START_FRAME not in data and FRAME_NUMBER not in data:
            data[START_FRAME] = data[TEMPORAL][0].get_attribute(FRAME_NUMBER)
            data[END_FRAME] = data[TEMPORAL][-1].get_attribute(FRAME_NUMBER)
            if data[START_FRAME] == data[END_FRAME]:
                data[FRAME_NUMBER] = START_FRAME
        super().__init__(**data)
        if self.temporal is None:
            self.temporal = []
            data[END_FRAME] = data[START_FRAME]
    
    def get_temporal(self, frame_number: int = None) -> Temporal:
        """
        Get the temporal object at a specific frame number
        """
        if frame_number is None:
            return self.temporal[-1]
        if frame_number < self.start_frame or frame_number > self.end_frame:
            return None
        return self.temporal[(frame_number - self.start_frame) // self.skip_frames]

    def get_static_attribute(self, key: str):
        """
        Get the static attribute of the object
        """
        return self.get_attribute(key)

    def get_temporal_attribute(self, key: str, frame_number: int):
        """
        Get the temporal attribute of the object at a specific frame number
        """
        temporal = self.get_temporal(frame_number)
        if temporal is None:
            return None
        return temporal.get_attribute(key)

    def append_temporal(self, temporal: Temporal):
        #Create a new tracked temporal object
        other_temporal_attrs = {k: v for k, v in temporal.dict().items() if k not in [BOUNDING_BOX, VELOCITY, FRAME_NUMBER]}
        if len(self.temporal) == 0:
            self.temporal = [Temporal(frame_number=self.start_frame, bounding_box=temporal.bounding_box, velocity=Point(x=0, y=0), **other_temporal_attrs)]
        else:
            last_temporal = self.temporal[-1]
            new_velocity = Point(x=temporal.center().x - last_temporal.center().x, y=temporal.center().y - last_temporal.center().y)
            tracked_temporal = Temporal(frame_number=self.get_attribute(START_FRAME)+ self.get_attribute(SKIP_FRAMES) , bounding_box=temporal.get_attribute(BOUNDING_BOX), velocity=new_velocity, **other_temporal_attrs)
            self.temporal.append(tracked_temporal)
            self.set_attribute(END_FRAME, self.get_attribute(END_FRAME) + self.get_attribute(SKIP_FRAMES))

    def set_temporal(self, temporal: Temporal, interpolate: bool = False):
        """
        Set the temporal object at a specific frame number
        
        If interpolate is True, then the object's BoundingBox will be interpolated between the previous and next frame
        """
        other_temporal_attrs = {k: v for k, v in temporal.dict().items() if k not in set([BOUNDING_BOX, FRAME_NUMBER, VELOCITY])} #Set the temporals in between to have the same other attrs as new
        frame_number = temporal.get_attribute(FRAME_NUMBER)
        start_frame = self.get_attribute(START_FRAME)
        end_frame = self.get_attribute(END_FRAME)
        skip_frames = self.get_attribute(SKIP_FRAMES)
        if frame_number < start_frame or frame_number > end_frame:
            if frame_number > end_frame and interpolate:
                #Set all linearly interpolated temporal objects between the last frame and the new temporal object
                last_bounding_box: BoundingBox = self.temporal[-1].get_attribute(BOUNDING_BOX)
                new_bounding_box: BoundingBox = temporal.get_attribute(BOUNDING_BOX)
                new_velocity = Point(x=temporal.center().x - self.temporal[-1].center().x, y=temporal.center().y - self.temporal[-1].center().y)
                for i in range(end_frame + skip_frames, frame_number + skip_frames, skip_frames):
                    interpolated_bounding_box = BoundingBox(
                        x1=last_bounding_box.x1 + (new_bounding_box.x1 - last_bounding_box.x1) * (i - end_frame) / (frame_number - end_frame), 
                        y1=last_bounding_box.y1 + (new_bounding_box.y1 - last_bounding_box.y1) * (i - end_frame) / (frame_number - end_frame), 
                        x2=last_bounding_box.x2 + (new_bounding_box.x2 - last_bounding_box.x2) * (i - end_frame) / (frame_number - end_frame), 
                        y2=last_bounding_box.y2 + (new_bounding_box.y2 - last_bounding_box.y2) * (i - end_frame) / (frame_number - end_frame)
                    )
                    new_temporal = Temporal(frame_number=i, bounding_box=interpolated_bounding_box, velocity=new_velocity, **other_temporal_attrs)
                    self.temporal.append(new_temporal)
                self.set_attribute(END_FRAME, frame_number)
            elif frame_number < start_frame and interpolate:
                #Set all linearly interpolated temporal objects between the first frame and the new temporal object
                first_bounding_box: BoundingBox = self.temporal[0].get_attribute(BOUNDING_BOX)
                new_bounding_box: BoundingBox = temporal.get_attribute(BOUNDING_BOX)
                new_velocity = Point(x = self.temporal[0].center().x - temporal.center().x, y = self.temporal[0].center().y - temporal.center().y)
                self.temporal[0].set_attribute(VELOCITY, new_velocity)
                for i in range(start_frame - skip_frames, frame_number - skip_frames, -skip_frames):
                    interpolated_bounding_box = BoundingBox(
                        x1=first_bounding_box.x1 + (new_bounding_box.x1 - first_bounding_box.x1) * (i - start_frame) / (frame_number - start_frame), 
                        y1=first_bounding_box.y1 + (new_bounding_box.y1 - first_bounding_box.y1) * (i - start_frame) / (frame_number - start_frame), 
                        x2=first_bounding_box.x2 + (new_bounding_box.x2 - first_bounding_box.x2) * (i - start_frame) / (frame_number - start_frame), 
                        y2=first_bounding_box.y2 + (new_bounding_box.y2 - first_bounding_box.y2) * (i - start_frame) / (frame_number - start_frame)
                    )
                    if i == frame_number - skip_frames:
                        new_velocity = 0
                    new_temporal = Temporal(frame_number=i, bounding_box=interpolated_bounding_box, velocity=new_velocity, **other_temporal_attrs)
                    self.temporal.insert(0, new_temporal)
                self.set_attribute(START_FRAME, frame_number)
            return
        self.temporal[(frame_number - start_frame) // skip_frames] = temporal
    
    def slice(self, start_frame: int = None, end_frame: int = None, frame_number: int = None):
        """
        Slice the temporal object to only include the frames between start_frame and end_frame
        """
        self_start_frame = self.get_attribute(START_FRAME)
        self_end_frame = self.get_attribute(END_FRAME)
        object_id = self.get_attribute(OBJECT_ID)
        skip_frames = self.get_attribute(SKIP_FRAMES)
        if frame_number is not None:
            if frame_number < self_start_frame or frame_number > self_end_frame:
                return None
            init_dict = {
                OBJECT_ID: object_id,
                START_FRAME: frame_number,
                END_FRAME: frame_number,
                SKIP_FRAMES: skip_frames,
                "temporal": self.temporal[(frame_number - self_start_frame) // skip_frames]
            }
            return SingleObject(**init_dict)
        if start_frame < self_start_frame or end_frame > self_end_frame:
            return None

        init_dict = {
            OBJECT_ID: object_id,
            START_FRAME: start_frame,
            END_FRAME: end_frame,
            SKIP_FRAMES: skip_frames,
            "temporal": self.temporal[(start_frame - self_start_frame) // skip_frames: (end_frame - self_start_frame) // skip_frames + 1]
        }
        return ObjectSlice(**init_dict)

class ObjectSlice(Object, extra = Extra.allow):
    """
    This is an object that contains the static info of an object and the temporal info of a slice of the object's temporal object
    """

    fields: ClassVar[Dict[str, type]] = {
        SLICE_END_FRAME: int,
        SLICE_START_FRAME: int,
    }

    def __init__(self, **data):
        if SLICE_START_FRAME not in data and SLICE_END_FRAME not in data and FRAME_NUMBER in data:
            data[SLICE_START_FRAME] = data[FRAME_NUMBER]
            data[SLICE_END_FRAME] = data[FRAME_NUMBER]
        if SLICE_START_FRAME not in data and START_FRAME in data:
            data[SLICE_START_FRAME] = data[START_FRAME]
        if SLICE_END_FRAME not in data and END_FRAME in data:
            data[SLICE_END_FRAME] = data[END_FRAME]
        if type(data[TEMPORAL]) != list:
            data[TEMPORAL] = [data[TEMPORAL]]
        super().__init__(**data)

    def get_temporal(self, frame_number: int = None) -> Temporal:
        """
        Get the temporal object at a specific frame number
        """
        if frame_number is None:
            return self.temporal[-1]

        start_frame = self.get_attribute(SLICE_START_FRAME)
        skip_frames = self.get_attribute(SKIP_FRAMES)
        end_frame = self.get_attribute(SLICE_END_FRAME)

        if frame_number < start_frame or frame_number > end_frame:
            return None
        return self.temporal[(frame_number - start_frame) // skip_frames]
    
    def set_temporal(self, temporal: Temporal, interpolate=False, extend=False): #TODO: Throw warning if frame number is not in slice
        """
        Set the temporal object at a specific frame number
        """
        other_temporal_attrs = {k: v for k, v in temporal.dict().items() if k not in set([BOUNDING_BOX, FRAME_NUMBER, VELOCITY])} 
        frame_number = temporal.get_attribute(FRAME_NUMBER)
        start_frame = self.get_attribute(SLICE_START_FRAME)
        end_frame = self.get_attribute(SLICE_END_FRAME)
        skip_frames = self.get_attribute(SKIP_FRAMES)
        if frame_number < start_frame or frame_number > end_frame:
            if frame_number > end_frame and interpolate:
                #Set all linearly interpolated temporal objects between the last frame and the new temporal object
                last_bounding_box: BoundingBox = self.temporal[-1].get_attribute(BOUNDING_BOX)
                new_bounding_box: BoundingBox = temporal.get_attribute(BOUNDING_BOX)
                new_velocity = Point(x=temporal.center().x - self.temporal[-1].center().x, y=temporal.center().y - self.temporal[-1].center().y)
                for i in range(end_frame + skip_frames, frame_number + skip_frames, skip_frames):
                    interpolated_bounding_box = BoundingBox(
                        x1=last_bounding_box.x1 + (new_bounding_box.x1 - last_bounding_box.x1) * (i - end_frame) / (frame_number - end_frame), 
                        y1=last_bounding_box.y1 + (new_bounding_box.y1 - last_bounding_box.y1) * (i - end_frame) / (frame_number - end_frame), 
                        x2=last_bounding_box.x2 + (new_bounding_box.x2 - last_bounding_box.x2) * (i - end_frame) / (frame_number - end_frame), 
                        y2=last_bounding_box.y2 + (new_bounding_box.y2 - last_bounding_box.y2) * (i - end_frame) / (frame_number - end_frame)
                    )
                    new_temporal = Temporal(frame_number=i, bounding_box=interpolated_bounding_box, velocity=new_velocity, **other_temporal_attrs)
                    self.temporal.append(new_temporal)
                self.set_attribute(SLICE_END_FRAME, frame_number)
                if extend and self.get_attribute(END_FRAME) < frame_number:
                    self.set_attribute(END_FRAME, frame_number)
            elif frame_number < start_frame and interpolate:
                #Set all linearly interpolated temporal objects between the first frame and the new temporal object
                first_bounding_box: BoundingBox = self.temporal[0].get_attribute(BOUNDING_BOX)
                new_bounding_box: BoundingBox = temporal.get_attribute(BOUNDING_BOX)
                new_velocity = Point(x = self.temporal[0].center().x - temporal.center().x, y = self.temporal[0].center().y - temporal.center().y)
                self.temporal[0].set_attribute(VELOCITY, new_velocity)
                for i in range(start_frame - skip_frames, frame_number - skip_frames, -skip_frames):
                    interpolated_bounding_box = BoundingBox(
                        x1=first_bounding_box.x1 + (new_bounding_box.x1 - first_bounding_box.x1) * (i - start_frame) / (frame_number - start_frame), 
                        y1=first_bounding_box.y1 + (new_bounding_box.y1 - first_bounding_box.y1) * (i - start_frame) / (frame_number - start_frame), 
                        x2=first_bounding_box.x2 + (new_bounding_box.x2 - first_bounding_box.x2) * (i - start_frame) / (frame_number - start_frame), 
                        y2=first_bounding_box.y2 + (new_bounding_box.y2 - first_bounding_box.y2) * (i - start_frame) / (frame_number - start_frame)
                    )
                    if i == frame_number - skip_frames:
                        new_velocity = 0
                    new_temporal = Temporal(frame_number=i, bounding_box=interpolated_bounding_box, velocity=new_velocity, **other_temporal_attrs)
                    self.temporal.insert(0, new_temporal)
                self.set_attribute(SLICE_START_FRAME, frame_number)
                if extend and self.get_attribute(START_FRAME) > frame_number:
                    self.set_attribute(START_FRAME, frame_number)
            return
        self.temporal[(frame_number - start_frame) // skip_frames] = temporal

class SingleObject(ObjectSlice, extra = Extra.allow):
    """
    This is an object that only contains a single temporal instance
    """

    fields: ClassVar[Dict[str, type]] = {
        FRAME_NUMBER: int
    }
    
    def __init__(self, **data):
        if type(data[TEMPORAL]) != list:
            data[TEMPORAL] = [data[TEMPORAL]]
        for i, val in enumerate(data[TEMPORAL]):
            if type(val) != Temporal and type(val) == dict:
                data[TEMPORAL][i] = Temporal(**val)
            elif type(val) != Temporal:
                raise TypeError("Temporal must be of type Temporal or dict to be converted to Temporal")
        if FRAME_NUMBER not in data:
            data[FRAME_NUMBER] = data[TEMPORAL][0].frame_number
        if START_FRAME not in data:
            data[START_FRAME] = data[TEMPORAL][0].frame_number
        if END_FRAME not in data:
            data[END_FRAME] = data[TEMPORAL][0].frame_number
        if SLICE_START_FRAME not in data:
            data[SLICE_START_FRAME] = data[TEMPORAL][0].frame_number
        if SLICE_END_FRAME not in data:
            data[SLICE_END_FRAME] = data[TEMPORAL][0].frame_number
        super().__init__(**data)
