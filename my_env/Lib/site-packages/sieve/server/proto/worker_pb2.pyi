from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class HealthStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEALTH_UNKNOWN: _ClassVar[HealthStatus]
    HEALTH_SERVING: _ClassVar[HealthStatus]
    HEALTH_SETUP: _ClassVar[HealthStatus]
    HEALTH_ERROR: _ClassVar[HealthStatus]

class SetupStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SETUP_UNKNOWN: _ClassVar[SetupStatus]
    SETUP_STARTED: _ClassVar[SetupStatus]
    SETUP_ERROR: _ClassVar[SetupStatus]
    SETUP_SUCCESS: _ClassVar[SetupStatus]
    SETUP_NODE_ERROR: _ClassVar[SetupStatus]
    SETUP_LOAD_ERROR: _ClassVar[SetupStatus]

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_SUCCEEDED: _ClassVar[Status]
    STATUS_FAILED: _ClassVar[Status]
    STATUS_PROCESSING: _ClassVar[Status]

HEALTH_UNKNOWN: HealthStatus
HEALTH_SERVING: HealthStatus
HEALTH_SETUP: HealthStatus
HEALTH_ERROR: HealthStatus
SETUP_UNKNOWN: SetupStatus
SETUP_STARTED: SetupStatus
SETUP_ERROR: SetupStatus
SETUP_SUCCESS: SetupStatus
SETUP_NODE_ERROR: SetupStatus
SETUP_LOAD_ERROR: SetupStatus
STATUS_SUCCEEDED: Status
STATUS_FAILED: Status
STATUS_PROCESSING: Status

class HealthCheckRequest(_message.Message):
    __slots__ = ("service", "kill")
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    KILL_FIELD_NUMBER: _ClassVar[int]
    service: str
    kill: bool

    def __init__(self, service: _Optional[str] = ..., kill: bool = ...) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("setup_info", "status", "killed")
    SETUP_INFO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    KILLED_FIELD_NUMBER: _ClassVar[int]
    setup_info: Setup
    status: HealthStatus
    killed: bool

    def __init__(
        self,
        setup_info: _Optional[_Union[Setup, _Mapping]] = ...,
        status: _Optional[_Union[HealthStatus, str]] = ...,
        killed: bool = ...,
    ) -> None: ...

class Setup(_message.Message):
    __slots__ = ("status", "retries", "time", "error")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RETRIES_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    status: SetupStatus
    retries: int
    time: float
    error: str

    def __init__(
        self,
        status: _Optional[_Union[SetupStatus, str]] = ...,
        retries: _Optional[int] = ...,
        time: _Optional[float] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...

class PredictionInput(_message.Message):
    __slots__ = ("key", "data", "file_server", "stop", "kill")
    KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    FILE_SERVER_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    KILL_FIELD_NUMBER: _ClassVar[int]
    key: str
    data: bytes
    file_server: str
    stop: bool
    kill: bool

    def __init__(
        self,
        key: _Optional[str] = ...,
        data: _Optional[bytes] = ...,
        file_server: _Optional[str] = ...,
        stop: bool = ...,
        kill: bool = ...,
    ) -> None: ...

class PredictionMetadata(_message.Message):
    __slots__ = ("override_cost_dollars",)
    OVERRIDE_COST_DOLLARS_FIELD_NUMBER: _ClassVar[int]
    override_cost_dollars: float

    def __init__(self, override_cost_dollars: _Optional[float] = ...) -> None: ...

class PredictionResponse(_message.Message):
    __slots__ = (
        "data",
        "status",
        "stop",
        "error",
        "key",
        "killed",
        "metadata",
        "fatal",
    )
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    KILLED_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    FATAL_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    status: Status
    stop: bool
    error: str
    key: str
    killed: bool
    metadata: PredictionMetadata
    fatal: bool

    def __init__(
        self,
        data: _Optional[bytes] = ...,
        status: _Optional[_Union[Status, str]] = ...,
        stop: bool = ...,
        error: _Optional[str] = ...,
        key: _Optional[str] = ...,
        killed: bool = ...,
        metadata: _Optional[_Union[PredictionMetadata, _Mapping]] = ...,
        fatal: bool = ...,
    ) -> None: ...
