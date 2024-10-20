from typing import List
from .base import Temporal, Track
import numpy as np
class Box(Temporal):
    """Class to store a box in Sieve."""
    x1: float
    y1: float
    x2: float
    y2: float
    frame: int
    cls: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if self.x1 is None or self.y1 is None or self.x2 is None or self.y2 is None:
            raise ValueError("All x and y coordinates must be set")

    def list(self):
        return [self.x1, self.y1, self.x2, self.y2]
    
    def array(self):
        return np.array(self.list())


class TrackedBox(Box, Track):
    """Class to store a tracked box in Sieve."""
    pass

class TrackedObject(Temporal, Track):
    """Class to store a tracked object in Sieve."""
    cls: str = ""
    boxes: List[TrackedBox] = []
