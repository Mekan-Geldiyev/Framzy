from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class ScalingRequest(_message.Message):
    __slots__ = ("model_id", "source")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    source: str

    def __init__(
        self, model_id: _Optional[str] = ..., source: _Optional[str] = ...
    ) -> None: ...

class ScalingInfo(_message.Message):
    __slots__ = ("queue_size", "currently_processing", "average_predict_time")
    QUEUE_SIZE_FIELD_NUMBER: _ClassVar[int]
    CURRENTLY_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_PREDICT_TIME_FIELD_NUMBER: _ClassVar[int]
    queue_size: int
    currently_processing: int
    average_predict_time: float

    def __init__(
        self,
        queue_size: _Optional[int] = ...,
        currently_processing: _Optional[int] = ...,
        average_predict_time: _Optional[float] = ...,
    ) -> None: ...

class ScalingEvent(_message.Message):
    __slots__ = ("previous_replicas", "new_replicas", "event_time", "scaling_info")
    PREVIOUS_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    NEW_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    EVENT_TIME_FIELD_NUMBER: _ClassVar[int]
    SCALING_INFO_FIELD_NUMBER: _ClassVar[int]
    previous_replicas: int
    new_replicas: int
    event_time: _timestamp_pb2.Timestamp
    scaling_info: ScalingInfo

    def __init__(
        self,
        previous_replicas: _Optional[int] = ...,
        new_replicas: _Optional[int] = ...,
        event_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        scaling_info: _Optional[_Union[ScalingInfo, _Mapping]] = ...,
    ) -> None: ...

class ScalingEvents(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[ScalingEvent]

    def __init__(
        self, events: _Optional[_Iterable[_Union[ScalingEvent, _Mapping]]] = ...
    ) -> None: ...

class ScalingResponse(_message.Message):
    __slots__ = ("did_scale", "cached", "event")
    DID_SCALE_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    did_scale: bool
    cached: bool
    event: ScalingEvent

    def __init__(
        self,
        did_scale: bool = ...,
        cached: bool = ...,
        event: _Optional[_Union[ScalingEvent, _Mapping]] = ...,
    ) -> None: ...
