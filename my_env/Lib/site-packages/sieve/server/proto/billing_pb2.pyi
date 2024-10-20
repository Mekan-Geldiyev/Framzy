from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class BillingRequest(_message.Message):
    __slots__ = (
        "organization_id",
        "model_id",
        "job_id",
        "run_id",
        "start_timestamp",
        "end_timestamp",
        "timestamp",
        "type",
        "machine_type",
        "split",
        "use_credits",
        "override_cost_dollars",
    )
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SPLIT_FIELD_NUMBER: _ClassVar[int]
    USE_CREDITS_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_COST_DOLLARS_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    model_id: str
    job_id: str
    run_id: str
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    timestamp: _timestamp_pb2.Timestamp
    type: str
    machine_type: str
    split: int
    use_credits: bool
    override_cost_dollars: float

    def __init__(
        self,
        organization_id: _Optional[str] = ...,
        model_id: _Optional[str] = ...,
        job_id: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
        start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        type: _Optional[str] = ...,
        machine_type: _Optional[str] = ...,
        split: _Optional[int] = ...,
        use_credits: bool = ...,
        override_cost_dollars: _Optional[float] = ...,
    ) -> None: ...

class BillingResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool

    def __init__(self, success: bool = ...) -> None: ...
