import numpy as np
# import time
from typing import List, Dict, ClassVar
from pydantic import validator, Extra, Field
import cv2
from .object import Temporal, StaticObject, Object, SingleObject, ObjectSlice
from .base import SieveBaseModel
from .constants import *
import urllib
import requests

class FrameTemporal(Temporal, arbitrary_types_allowed=True):
    """
    A frame temporal object is a temporal object that contains image data
    """

    fields: ClassVar[Dict[str, type]] = {
        FRAME_NUMBER: int,
        FRAME_DATA: bytes,
        FRAME_FORMAT: str
    }

    defaults: ClassVar[Dict[str, Field]] = {
        FRAME_FORMAT: ".png"
    }

    def get_array(self):
        """
        Returns the stored image as a numpy array
        """
        return cv2.imdecode(np.frombuffer(self.data, np.uint8), cv2.IMREAD_UNCHANGED)

    @validator(CLASS, check_fields=False)
    def check_valid(cls, v):
        """
        Checks if the data is a valid bytearray
        """
        if type(v) != bytes:
            raise ValueError("must be bytes")
        return v

    # Don't print the data
    def __repr__(self):
        return f"FrameTemporal(frame_number={self.frame_number}, format={self.format})"
    
    def __str__(self):
        return self.__repr__()

class FrameStaticObject(StaticObject, extra=Extra.allow):
    """
    A frame static object is a special static data containing static attributes of the frame like fps, width, height, etc.
    """

    fields: ClassVar[Dict[str, type]] = {
        FPS: float,
        WIDTH: int,
        HEIGHT: int,
        SOURCE_URL: str,
        SOURCE_TYPE: str,
        CLASS: str
    }

    defaults: ClassVar[Dict[str, Field]] = {
        SOURCE_TYPE: None,
        CLASS: "frame",
        SOURCE_URL: None
    }

    def __repr__(self):
        return f"FrameStaticObject(fps={self.fps}, width={self.width}, height={self.height}, source_url={self.source_url}, source_type={self.source_type})"
    
    def __str__(self):
        return self.__repr__()

    @validator(CLASS, allow_reuse=True, check_fields=False)
    def check_valid(cls, v):
        """
        Makes sure the class is frame
        """
        if v != "frame":
            raise ValueError("must be 'frame'")
        return v

    @validator(FPS, allow_reuse=True, check_fields=False)
    def check_valid(cls, v):
        """
        Checks if the fps is a valid float
        """
        if type(v) != float:
            raise ValueError("must be float")
        return v

class FrameObject(Object, FrameStaticObject, extra=Extra.allow):
    """
    A frame object is a special object that contains all the information about a frame
    """
    fields: ClassVar[Dict[str, type]] = {
        TEMPORAL: List[FrameTemporal]
    }

class FrameObjectSlice(FrameObject, ObjectSlice, extra=Extra.allow):
    """
    A frame object slice is a special single object that contains all the information about a frame + a single temporal object
    """
    fields: ClassVar[Dict[str, type]] = {
        TEMPORAL: List[FrameTemporal]
    }

    
class FrameSingleObject(FrameObjectSlice, SingleObject, extra=Extra.allow):
    """
    A frame single object is a special single object that contains all the information about a frame + a single temporal object
    """

    fields: ClassVar[Dict[str, type]] = {
        TEMPORAL: List[FrameTemporal]
    }

class FrameFetcher(SieveBaseModel, extra=Extra.allow, arbitrary_types_allowed=True):
    """
    A video is a special class that allows you to directly access the video and image data
    """

    fields: ClassVar[Dict[str, type]] = {
        FPS: float,
        WIDTH: int,
        HEIGHT: int,
        SOURCE_URL: str,
        SOURCE_TYPE: str,
        NUM_CHANNELS: int,
        "fetcher_url": str
    }

    defaults: ClassVar[Dict[str, Field]] = {
        NUM_CHANNELS: 3
    }

    # Fields with defaults as

    def init_cap(self):
        if self.source_type == "video":
            if "fetcher_url" not in self.__dict__:
                self._cap = cv2.VideoCapture(self.source_url)
                self._cur_frame = 0
        elif self.source_type == "image":
            self._cap = None
            self._cur_frame = 0

    def seek_to_frame(self, frame_number):
        if self.source_type == "image":
            return
        if "fetcher_url" in self.__dict__:
            self._cur_frame = frame_number
            return 
        if frame_number < self._cur_frame or frame_number > self._cur_frame + 100:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self._cur_frame = frame_number
        else:
            while self._cur_frame < frame_number:
                ret, frame = self._cap.read()
                self._cur_frame += 1

    def get_current_frame_number(self):
        return self._cur_frame

    def get_frame(self, frame_number=None):
        if frame_number is None:
            frame_number = self._cur_frame
        if self.source_type == "image":
            req = urllib.request.urlopen(self.source_url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            frame = cv2.imdecode(arr, -1)
            return frame
        self.seek_to_frame(frame_number)
        if "fetcher_url" in self.__dict__:
            print("fetching frame from file server", frame_number)
            try:
                req = requests.post(self.fetcher_url, data={"frame": frame_number, "video_url": self.source_url, "fps": self.fps}, timeout=3)
            except requests.exceptions.Timeout:
                raise Exception("Timeout while fetching frame, internal error")
            except requests.exceptions.ConnectionError:
                raise Exception("Connection error while fetching frame, internal error")
            arr = np.asarray(bytearray(req.content), dtype=np.uint8)
            frame = cv2.imdecode(arr, -1)
            if frame is None:
                print("failed to fetch frame", frame_number)
                return np.zeros((self.height, self.width, 3), np.uint8)
            return frame
        ret, frame = self._cap.read()
        self._cur_frame += 1
        if ret:
            return frame
        return np.zeros((self.height, self.width, 3), np.uint8)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle baz
        del_fields = ['_cap']
        for del_field in del_fields:
            if del_field in state:
                del state[del_field]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Create cap object
        self._cap = cv2.VideoCapture(self.source_url)
        self._cur_frame = 0


