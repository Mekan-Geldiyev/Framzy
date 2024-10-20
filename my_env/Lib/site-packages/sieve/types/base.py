from pydantic.v1 import BaseModel, Field, Extra
from typing import List, Any
import uuid


class Struct(BaseModel, extra=Extra.allow):
    """Base class for all types in Sieve."""

    def __init__(__pydantic_self__, **data: Any) -> None:
        """Override __init__ to allow for extra fields"""
        super().__init__(**data)

    def __init_subclass__(cls):
        """Override __init_subclass__ to remove validators from all fields"""

        super().__init_subclass__()
        for field in cls.__fields__.values():
            try:
                field.validators = []
            except AttributeError:
                pass
