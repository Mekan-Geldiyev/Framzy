from .base import SieveBaseModel
from pydantic import validator, Extra
import numpy as np
from typing import Dict, Any

class Point(SieveBaseModel, validate_assignment=True):
    """
    A point is a 2D point in space
    """
    x: float
    y: float
    def get_array(self):
        """
        Returns the point as a numpy array
        """
        return np.array(self.get_list())
    def from_array(array: np.ndarray):
        """
        Creates a point from a numpy array
        """
        if len(array) != 2:
            raise ValueError("array must have length 2")
        return Point(x=array[0], y=array[1])

    def get_list(self):
        return [self.x, self.y] 

class BoundingBox(SieveBaseModel, validate_assignment=True):
    """
    A bounding box is a 2D box in space that denotes the location of an object
    """
    x1: float
    y1: float
    x2: float
    y2: float
    def get_list(self):
        return [self.x1, self.y1, self.x2, self.y2]
    def get_array(self):
        return np.array(self.get_list())
    def from_array(array: np.ndarray):
        if len(array) != 4:
            raise ValueError("array must have length 4")
        return BoundingBox(x1=array[0], y1=array[1], x2=array[2], y2=array[3])
    def center(self) -> Point:
        return Point(x=(self.x1 + self.x2) / 2, y=(self.y1 + self.y2) / 2)
    @validator('x1', 'y1', 'x2', 'y2')
    def check_valid(cls, v):
        if type(v) != float:
            raise TypeError("must be float")
        return v

class UserMetadata(SieveBaseModel):
    pass