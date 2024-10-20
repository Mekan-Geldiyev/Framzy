from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR: _ClassVar[ResponseType]
    TIMEOUT: _ClassVar[ResponseType]
    OK: _ClassVar[ResponseType]

ERROR: ResponseType
TIMEOUT: ResponseType
OK: ResponseType

class GetOutputsRequest(_message.Message):
    __slots__ = ("model_id", "run_id", "job_id")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    run_id: str
    job_id: str

    def __init__(
        self,
        model_id: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
        job_id: _Optional[str] = ...,
    ) -> None: ...

class Output(_message.Message):
    __slots__ = ("stop", "error", "value", "status", "run_id")
    STOP_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    stop: bool
    error: str
    value: str
    status: ResponseType
    run_id: str

    def __init__(
        self,
        stop: bool = ...,
        error: _Optional[str] = ...,
        value: _Optional[str] = ...,
        status: _Optional[_Union[ResponseType, str]] = ...,
        run_id: _Optional[str] = ...,
    ) -> None: ...

class File(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: bytes

    def __init__(self, content: _Optional[bytes] = ...) -> None: ...

class FileChunk(_message.Message):
    __slots__ = ("content", "end_of_file")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    END_OF_FILE_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    end_of_file: bool

    def __init__(
        self, content: _Optional[bytes] = ..., end_of_file: bool = ...
    ) -> None: ...

class GetFileRequest(_message.Message):
    __slots__ = ("file_hash",)
    FILE_HASH_FIELD_NUMBER: _ClassVar[int]
    file_hash: str

    def __init__(self, file_hash: _Optional[str] = ...) -> None: ...

class GetFileStreamRequest(_message.Message):
    __slots__ = ("file_hash",)
    FILE_HASH_FIELD_NUMBER: _ClassVar[int]
    file_hash: str

    def __init__(self, file_hash: _Optional[str] = ...) -> None: ...
