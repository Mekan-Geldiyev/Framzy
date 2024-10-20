from pathlib import Path
from urllib.parse import urlparse
from .base import Struct
from pydantic.v1 import Extra, validate_arguments
from pydantic import AnyHttpUrl, HttpUrl, TypeAdapter, ValidationError
from io import BytesIO
import requests
import warnings
import uuid
import os

from pydantic.v1 import Field
import tempfile
from typing import Optional, Union, Callable, Any, no_type_check
import inspect
import base64
from ..api.constants import API_URL, API_BASE
from ..server.proto import server_pb2, server_pb2_grpc
import grpc


class OpenCVNotInstalledException(Exception):
    """Exception to raise when OpenCV is not installed"""

    def __init__(self, functionality: str):
        self.functionality = functionality
        super().__init__(
            f"OpenCV is not installed, but is required for {functionality}. Please install opencv-python-headless or opencv-python as a python dependency. In addition, please install libgl1-mesa-glx (LibGL.1) as a system package."
        )


class NumpyNotInstalledException(Exception):
    """Exception to raise when Numpy is not installed"""

    def __init__(self, functionality: str):
        self.functionality = functionality
        super().__init__(
            f"Numpy is not installed, but is required for {functionality}. Please install numpy as a python dependency."
        )


def create_fileservice_grpc_stub(api_url):
    api_host = api_url.split("//")[1]
    options = [("grpc.keepalive_time_ms", 10000)]

    if api_url.startswith("https://"):
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(f"{api_host}:443", credentials, options=options)
    else:
        channel = grpc.insecure_channel(f"{api_host}:80", options=options)
    stub = server_pb2_grpc.FileServiceStub(channel)
    return stub


class NoSetterException(Exception):
    """Exception to raise when no setter is found for attribute"""

    pass


import time


def download_from_file_server(obj):
    if obj._internal is None or obj._internal.get("fileserver_sha256") is None:
        return None
    file_hash = obj._internal["fileserver_sha256"]
    api_url = os.environ.get("SIEVE_API_URL", API_URL)
    stub = create_fileservice_grpc_stub(api_url)

    max_retries = 5
    attempt = 0
    while attempt < max_retries:
        try:
            responses = stub.GetFileStream(
                server_pb2.GetFileStreamRequest(file_hash=file_hash)
            )
            suffix = (
                "file_suffix" in obj._internal and obj._internal["file_suffix"] or None
            )
            if suffix is not None and suffix[0] != ".":
                suffix = "." + suffix
            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                dir="/mountedssd" if os.path.exists("/mountedssd") else None,
                delete=False,
                mode='wb'
            ) as f:
                local_filename = f.name
                for response in responses:
                    if response.content:
                        f.write(response.content)
            return local_filename
        except grpc.RpcError as e:
            decorated_exception = f"Internal gRPC error occurred: {e.code().name} - {e.details()}"
            if (
                e.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                or e.code() == grpc.StatusCode.UNAVAILABLE
                or e.code() == grpc.StatusCode.UNKNOWN
                or e.code() == grpc.StatusCode.INTERNAL
            ):
                pass
            else:
                raise Exception(decorated_exception) from e

            if attempt == max_retries - 1:
                raise Exception(decorated_exception) from e
            attempt += 1
            time.sleep(2**attempt)  # Exponential backoff
        except Exception as e:
            decorated_exception = f"An unexpected internal error occurred: {str(e)}"
            raise Exception(decorated_exception) from e
    return None


def download_file(url):
    """Download file from url and return path to file"""

    urlsuffix = url.split("?")[0].split("/")[-1]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    }  # To avoid 403
    with tempfile.NamedTemporaryFile(
        suffix=urlsuffix, dir="/mountedssd" if os.path.exists("/mountedssd") else None, delete=False, mode='wb'
    ) as f:
        local_filename = f.name
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


class File(Struct):
    """
    Base class for all types that have file information to store/load in Sieve.

    :param url: URL to file
    :type url: str
    :param path: Path to file
    :type path: str
    """

    url: str = None
    _path: str = None

    def __str__(self):
        fields = []
        if self.url is not None:
            fields += [f"url='{self.url}'"]
        if self._path is not None:
            fields += [f"path='{self._path}'"]
        if (
            len(fields) == 0
            and hasattr(self, "_internal")
            and self._internal is not None
        ):
            fields += [
                f"detail='File stored remotely to save storage. Please use .path to download'"
            ]

        fieldString = ", ".join(fields)
        return f"sieve.{type(self).__name__}({fieldString})"

    def __repr__(self):
        return self.__str__()

    def __init__(
        self,
        path_or_url: Union[str, Path, None] = None,
        path: Optional[str] = None,
        url: Optional[str] = None,
        **data,
    ):
        """Create a File object with path or url as input"""

        # TODO: Add deprecation close to end of 2024
        # if data:
        #     warnings.warn(
        #         "Using the File class to set additional attributes is deprecated.",
        #         DeprecationWarning,
        #     )

        if "_path" in data:
            if path is None:
                path = data["_path"]
            del data["_path"]

        if path_or_url is not None:
            if path or url:
                raise ValueError("Please provide either _fileurl, or path or url")
            if isinstance(path_or_url, Path):
                super().__init__(_path=str(path_or_url), **data)
            else:
                try:
                    TypeAdapter(HttpUrl).validate_python(path_or_url)
                    super().__init__(url=path_or_url, **data)
                except ValidationError:
                    super().__init__(_path=path_or_url, **data)
        elif (path is None) and (url is None):
            raise ValueError("Please provide either _fileurl, or path or url")
        else:
            if path and url:
                print(
                    "Warning: Both path and url are provided. Sieve will use path by default."
                )

            super().__init__(_path=path, url=url, **data)

    @property
    def path(self):
        """Return path to file as property"""

        if self._path is not None:
            return self._path
        if self.url is not None:
            self._path = download_file(self.url)
            return self._path
        elif hasattr(self, "_internal") and self._internal is not None:
            file_name = download_from_file_server(self)
            self._path = file_name
            if file_name is None:
                raise ValueError("Could not get file")
            return file_name
        raise ValueError("Either url or path must be set")


class Array(File, extra=Extra.allow):
    """
    Class to store and load an array in Sieve.

    :param array: Array to store
    :type array: np.ndarray
    :param url: URL to file
    :type url: str
    :param path: Path to file
    :type path: str
    """

    _path: str = None
    url: str = None
    _data: Optional[bytes] = None

    def __init__(self, array=None, **data):
        """Override __init__ to add _array if not present and array present"""
        super().__init__(**data)
        if array is not None:
            self._array = array
        else:
            self._array = None

    @property
    def data(self):
        """Return data as property, populate it if not present and other fields present"""

        if hasattr(self, "_data") and self._data is not None:
            return self._data
        elif self._array is not None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException(
                    "sieve.Array.data with an in memory array"
                )
            with BytesIO() as f:
                np.save(f, self._array)
                f.seek(0)
                self._data = f.read()
            return self._data
        elif self.url is not None:
            self._path = download_file(self.url)
            with open(self._path, "rb") as f:
                self._data = f.read()
            return self._data
        return None

    @data.setter
    def data(self, data):
        self._data = data
        if self._array is None:
            with BytesIO() as f:
                f.write(self._data)
                f.seek(0)
                try:
                    import numpy as np
                except ImportError:
                    raise NumpyNotInstalledException(
                        "sieve.Array.data with an in memory array"
                    )
                self._array = np.load(f)

    @property
    def path(self):
        """Return path to file as property, populate it if not present and other fields present"""

        if self._path is not None:
            return self._path
        elif self.url is not None:
            self._path = download_file(self.url)
            return self._path
        elif hasattr(self, "_array") and self._array is not None:
            with tempfile.NamedTemporaryFile(
                suffix=".npy",
                dir="/mountedssd" if os.path.exists("/mountedssd") else None,
                delete=False
            ) as f:
                self._path = f.name
                try:
                    import numpy as np
                except ImportError:
                    raise NumpyNotInstalledException(
                        "sieve.Array.path with an in memory array"
                    )
                np.save(self._path, self._array)
            return self._path
        elif self._data is not None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException(
                    "sieve.Array.path with an in memory array"
                )
            with tempfile.NamedTemporaryFile(
                suffix=".npy",
                dir="/mountedssd" if os.path.exists("/mountedssd") else None,
                delete=False
            ) as f:
                # Convert to array and save
                with BytesIO() as buffer:
                    buffer.write(self._data)
                    buffer.seek(0)
                    self._array = np.load(buffer)
                self._path = f.name
                np.save(self._path, self._array)
            return self._path
        elif hasattr(self, "_internal") and self._internal is not None:
            file_name = download_from_file_server(self)
            self._path = file_name
            if file_name is None:
                raise ValueError("Could not get file")
            return file_name
        raise ValueError("Either url, path, data or array must be set")

    @property
    def array(self):
        if hasattr(self, "_array") and self._array is not None:
            return self._array
        elif self._data is not None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException("sieve.Array.array")
            with BytesIO() as f:
                f.write(self._data)
                f.seek(0)
                self._array = np.load(f)
            return self._array
        elif self._path is not None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException("sieve.Array.array")
            self._array = np.load(self._path)
            return self._array
        elif self.url is not None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException("sieve.Array.array")
            self._path = download_file(self.url)
            self._array = np.load(self._path)
            return self._array
        raise ValueError("Either url, path, data or array must be set")

    def __str__(self):
        fields = []
        if self.url is not None:
            fields += [f"url='{self.url}'"]
        if self._path is not None:
            fields += [f"path='{self._path}'"]
        if hasattr(self, "_array") and self._array is not None:
            field = str(self._array)
            fields += [f"array={field}"]
        elif self._data is not None:
            fields += [f"data=[binary data]"]
        if (
            len(fields) == 0
            and hasattr(self, "_internal")
            and self._internal is not None
        ):
            fields += [
                f"detail='File stored remotely to save storage. Please use .path to download'"
            ]

        fieldString = ", ".join(fields)
        return f"sieve.{type(self).__name__}({fieldString})"

    # Set array
    @array.setter
    def array(self, array):
        self._array = array
        if self._data is None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException("sieve.Array.array")
            with BytesIO() as f:
                np.save(f, self._array)
                f.seek(0)
                self._data = f.read()

    @property
    def height(self):
        return self.array.shape[0]

    @property
    def width(self):
        return self.array.shape[1]

    @no_type_check
    def __setattr__(self, name, value):
        """To be able to use properties with setters"""

        try:
            setters = inspect.getmembers(
                self.__class__,
                predicate=lambda x: isinstance(x, property) and x.fset is not None,
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise NoSetterException("No setter found")
        except NoSetterException as e:
            super().__setattr__(name, value)

    def dict(
        self,
        *,
        include: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        exclude: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        if exclude is None:
            exclude = {"_array", "array", "_data"}
        else:
            exclude.add("_array")
            exclude.add("array")
            exclude.add("_data")
        if hasattr(self, "_array") and self._array is not None and self.data is None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException("sieve.Array")
            with BytesIO() as f:
                np.save(f, self._array)
                f.seek(0)
                self._data = f.read()
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        exclude: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> str:
        if exclude is None:
            exclude = {"_array", "array", "_data"}
        else:
            exclude.add("_array")
            exclude.add("array")
            exclude.add("_data")
        if hasattr(self, "_array") and self._array is not None and self.data is None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException(
                    "sieve.Array.json with an in memory array"
                )
            with BytesIO() as f:
                np.save(f, self._array)
                f.seek(0)
                self._data = f.read()
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            **dumps_kwargs,
        )


class Image(Array, extra=Extra.allow, arbitrary_types_allowed=True):
    """
    Class to store and load an image in Sieve.

    :param array: Array to store
    :type array: np.ndarray
    :param url: URL to file
    :type url: str
    :param path: Path to file
    :type path: str
    """

    _data: Optional[bytes] = None

    @property
    def array(self):
        """Return array as property, populate it if not present and other fields present"""

        if hasattr(self, "_array") and self._array is not None:
            return self._array
        elif self._data is not None:
            try:
                import numpy as np
            except ImportError:
                raise NumpyNotInstalledException(
                    "sieve.Image.array with in memory data"
                )
            try:
                import cv2
            except ImportError:
                raise OpenCVNotInstalledException(
                    "sieve.Image.array with in memory data"
                )
            a = cv2.imdecode(np.frombuffer(self._data, np.uint8), cv2.IMREAD_UNCHANGED)
            if a is None:
                raise Exception("Could not decode image")
            return a
        try:
            import cv2
        except ImportError:
            raise OpenCVNotInstalledException("sieve.Image.array with path")
        try:
            self._array = cv2.imread(self.path)
        except:
            raise ValueError("Invalid image path specified")
        return self._array

    # Set array
    @array.setter
    def array(self, array):
        self._array = array

    @property
    def data(self):
        """Return data as property, populate it if not present and other fields present"""

        if hasattr(self, "_data") and self._data is not None:
            return self._data
        elif hasattr(self, "_array") and self._array is not None:
            try:
                import cv2
            except ImportError:
                raise OpenCVNotInstalledException(
                    "sieve.Image.data with an in memory array"
                )
            self._data = cv2.imencode(".bmp", self._array)[1].tobytes()
            return self._data
        return None

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def path(self):
        """Return path to file as property, populate it if not present and other fields present"""
        if self._path is not None:
            return self._path
        elif self.url is not None:
            self._path = download_file(self.url)
            return self._path
        elif hasattr(self, "_array") and self._array is not None:
            try:
                import cv2
            except ImportError:
                raise OpenCVNotInstalledException(
                    "sieve.Image.path with an in memory array"
                )

            with tempfile.NamedTemporaryFile(
                suffix=".bmp",
                dir="/mountedssd" if os.path.exists("/mountedssd") else None,
                delete=False
            ) as f:
                local_filename = f.name
                cv2.imwrite(local_filename, self._array)
            return local_filename
        elif self._data is not None:
            with tempfile.NamedTemporaryFile(
                suffix=".bmp",
                dir="/mountedssd" if os.path.exists("/mountedssd") else None,
                delete=False
            ) as f:
                local_filename = f.name
                with open(local_filename, "wb") as file:
                    file.write(self._data)
            return local_filename
        elif hasattr(self, "_internal") and self._internal is not None:
            file_name = download_from_file_server(self)
            self._path = file_name
            if file_name is None:
                raise ValueError("Could not get file")
            return file_name
        raise ValueError("Either url, path, data or array must be set")

    @property
    def height(self):
        return self.array.shape[0]

    @property
    def width(self):
        return self.array.shape[1]

    @property
    def channels(self):
        if len(self.array.shape) < 3:
            return 1
        return self.array.shape[2]

    def __getstate__(self):
        """Override __getstate__ to remove array from pickle to avoid error"""

        state = super().__getstate__()
        # Don't pickle cap
        del_fields = ["_array"]
        for del_field in del_fields:
            if del_field in state.get("__dict__", {}):
                del state["__dict__"][del_field]
        return state

    @no_type_check
    def __setattr__(self, name, value):
        """To be able to use properties with setters"""

        try:
            setters = inspect.getmembers(
                self.__class__,
                predicate=lambda x: isinstance(x, property) and x.fset is not None,
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise NoSetterException("No setter found")
        except NoSetterException as e:
            super().__setattr__(name, value)

    def dict(
        self,
        *,
        include: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        exclude: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        """Override dict to remove array and data from dict to avoid error"""

        if exclude is None:
            exclude = {"_array", "array", "data", "_data"}
        else:
            exclude.add("_array")
            exclude.add("array")
            exclude.add("data")
            exclude.add("_data")
        if hasattr(self, "_array") and self._array is not None and self.data is None:
            # Calling self.data will encode the array
            pass
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        exclude: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> str:
        """Override json to remove array and data from json to avoid error"""

        if exclude is None:
            exclude = {"_array", "array", "data", "_data"}
        else:
            exclude.add("_array")
            exclude.add("array")
            exclude.add("data")
            exclude.add("_data")
        if hasattr(self, "_array") and self._array is not None and self.data is None:
            # Calling self.data will encode the array
            pass
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            **dumps_kwargs,
        )


class Video(File, extra=Extra.allow):
    """
    Class to store and load video in Sieve.

    :param url: URL to file
    :type url: str
    :param path: Path to file
    :type path: str
    """

    @property
    def cap(self):
        """Return video capture object as property, populate it if not present and other fields present"""
        try:
            import cv2
        except ImportError:
            raise OpenCVNotInstalledException("sieve.Video.cap")

        if hasattr(self, "_cap") and self._cap is not None:
            return self._cap
        if self._path is not None:
            self._cap = cv2.VideoCapture(self.path)
        else:
            self._cap = cv2.VideoCapture(self.url)
        return self._cap

    @property
    def fps(self):
        try:
            import cv2
        except ImportError:
            raise OpenCVNotInstalledException("sieve.Video.fps")

        return self.cap.get(cv2.CAP_PROP_FPS)

    @property
    def frame_count(self):
        try:
            import cv2
        except ImportError:
            raise OpenCVNotInstalledException("sieve.Video.frame_count")

        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def width(self):
        try:
            import cv2
        except ImportError:
            raise OpenCVNotInstalledException("sieve.Video.width")

        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        try:
            import cv2
        except ImportError:
            raise OpenCVNotInstalledException("sieve.Video.height")

        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def channels(self):
        return 3

    def __getstate__(self):
        """Override __getstate__ to remove cap from pickle to avoid error"""

        state = super().__getstate__()
        del_fields = ["_cap"]
        for del_field in del_fields:
            if del_field in state.get("__dict__", {}):
                del state["__dict__"][del_field]
        return state

    def dict(
        self,
        *,
        include: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        exclude: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        """Override dict to remove cap from dict to avoid error"""

        if exclude is None:
            exclude = {"_cap"}
        else:
            exclude.add("_cap")
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        exclude: Optional[Union["AbstractSetIntStr", "MappingIntStrAny"]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        models_as_dict: bool = True,
        **dumps_kwargs: Any,
    ) -> str:
        """Override json to remove cap from json to avoid error"""

        if exclude is None:
            exclude = {"_cap"}
        else:
            exclude.add("_cap")
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs,
        )


class Audio(File, extra=Extra.allow):
    """Class to store and load audio in Sieve."""
