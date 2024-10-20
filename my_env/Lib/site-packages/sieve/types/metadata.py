from typing import Optional, Union
from pydantic.v1 import BaseModel
from .file import Image


class Metadata(BaseModel):
    """Class to store public metadata in Sieve."""

    title: str = ""
    description: str = ""
    code_url: str = ""
    tags: list = []
    readme: str = ""
    public: bool = False
    image: Image = None
