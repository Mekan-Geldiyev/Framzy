from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StorageRequest(_message.Message):
    __slots__ = ("key", "data", "organization_id", "job_id", "run_id")
    KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    key: int
    data: bytes
    organization_id: str
    job_id: str
    run_id: str

    def __init__(
        self,
        key: _Optional[int] = ...,
        data: _Optional[bytes] = ...,
        organization_id: _Optional[str] = ...,
        job_id: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
    ) -> None: ...

class StorageResponse(_message.Message):
    __slots__ = ("key", "data")
    KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    key: int
    data: bytes

    def __init__(
        self, key: _Optional[int] = ..., data: _Optional[bytes] = ...
    ) -> None: ...
