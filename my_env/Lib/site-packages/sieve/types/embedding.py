from typing import List
from .base import Struct
class Embedding(Struct):
    """Class to store an embedding in Sieve."""
    embedding: List[float]
    metadata: dict = {}