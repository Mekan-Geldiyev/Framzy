from google.protobuf import timestamp_pb2 as _timestamp_pb2
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

class PodStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTAINER_CREATING: _ClassVar[PodStatus]
    SETUP: _ClassVar[PodStatus]
    IDLE: _ClassVar[PodStatus]
    PREDICTING: _ClassVar[PodStatus]
    TERMINATING: _ClassVar[PodStatus]
    ERROR: _ClassVar[PodStatus]
    HEART_BEAT: _ClassVar[PodStatus]

CONTAINER_CREATING: PodStatus
SETUP: PodStatus
IDLE: PodStatus
PREDICTING: PodStatus
TERMINATING: PodStatus
ERROR: PodStatus
HEART_BEAT: PodStatus

class Event(_message.Message):
    __slots__ = (
        "key",
        "ts",
        "dummy_event_data",
        "scale_event_data",
        "pod_status_event_data",
        "job_event_data",
    )
    KEY_FIELD_NUMBER: _ClassVar[int]
    TS_FIELD_NUMBER: _ClassVar[int]
    DUMMY_EVENT_DATA_FIELD_NUMBER: _ClassVar[int]
    SCALE_EVENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POD_STATUS_EVENT_DATA_FIELD_NUMBER: _ClassVar[int]
    JOB_EVENT_DATA_FIELD_NUMBER: _ClassVar[int]
    key: str
    ts: _timestamp_pb2.Timestamp
    dummy_event_data: DummyEvent
    scale_event_data: ScaleEvent
    pod_status_event_data: PodStatusEvent
    job_event_data: JobEvent

    def __init__(
        self,
        key: _Optional[str] = ...,
        ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        dummy_event_data: _Optional[_Union[DummyEvent, _Mapping]] = ...,
        scale_event_data: _Optional[_Union[ScaleEvent, _Mapping]] = ...,
        pod_status_event_data: _Optional[_Union[PodStatusEvent, _Mapping]] = ...,
        job_event_data: _Optional[_Union[JobEvent, _Mapping]] = ...,
    ) -> None: ...

class DummyEvent(_message.Message):
    __slots__ = ("test_data",)
    TEST_DATA_FIELD_NUMBER: _ClassVar[int]
    test_data: str

    def __init__(self, test_data: _Optional[str] = ...) -> None: ...

class EventStatus(_message.Message):
    __slots__ = ()

    def __init__(self) -> None: ...

class ScaleEvent(_message.Message):
    __slots__ = ("model_id", "num_replicas")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    num_replicas: int

    def __init__(
        self, model_id: _Optional[str] = ..., num_replicas: _Optional[int] = ...
    ) -> None: ...

class PodStatusEvent(_message.Message):
    __slots__ = (
        "model_id",
        "pod_id",
        "pod_status",
        "id",
        "container_index",
        "split",
        "node_id",
        "machine_type",
        "event_metadata",
    )
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    POD_STATUS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_INDEX_FIELD_NUMBER: _ClassVar[int]
    SPLIT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    pod_id: str
    pod_status: PodStatus
    id: str
    container_index: int
    split: int
    node_id: str
    machine_type: str
    event_metadata: PodStatusEventMetadata

    def __init__(
        self,
        model_id: _Optional[str] = ...,
        pod_id: _Optional[str] = ...,
        pod_status: _Optional[_Union[PodStatus, str]] = ...,
        id: _Optional[str] = ...,
        container_index: _Optional[int] = ...,
        split: _Optional[int] = ...,
        node_id: _Optional[str] = ...,
        machine_type: _Optional[str] = ...,
        event_metadata: _Optional[_Union[PodStatusEventMetadata, _Mapping]] = ...,
    ) -> None: ...

class PodStatusEventMetadata(_message.Message):
    __slots__ = ("description",)
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    description: str

    def __init__(self, description: _Optional[str] = ...) -> None: ...

class JobEvent(_message.Message):
    __slots__ = ("job_id", "job_status_change_event_data", "job_new_output_event_data")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_STATUS_CHANGE_EVENT_DATA_FIELD_NUMBER: _ClassVar[int]
    JOB_NEW_OUTPUT_EVENT_DATA_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    job_status_change_event_data: JobStatusChangeEvent
    job_new_output_event_data: JobNewOutputEvent

    def __init__(
        self,
        job_id: _Optional[str] = ...,
        job_status_change_event_data: _Optional[
            _Union[JobStatusChangeEvent, _Mapping]
        ] = ...,
        job_new_output_event_data: _Optional[_Union[JobNewOutputEvent, _Mapping]] = ...,
    ) -> None: ...

class JobStatusChangeEvent(_message.Message):
    __slots__ = ("job_status",)
    JOB_STATUS_FIELD_NUMBER: _ClassVar[int]
    job_status: str

    def __init__(self, job_status: _Optional[str] = ...) -> None: ...

class JobNewOutputEvent(_message.Message):
    __slots__ = ("output_key",)
    OUTPUT_KEY_FIELD_NUMBER: _ClassVar[int]
    output_key: int

    def __init__(self, output_key: _Optional[int] = ...) -> None: ...
