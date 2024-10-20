from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StopWorkRequest(_message.Message):
    __slots__ = ("reply_address",)
    REPLY_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    reply_address: str

    def __init__(self, reply_address: _Optional[str] = ...) -> None: ...

class StopWorkReply(_message.Message):
    __slots__ = ("response_code",)
    RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    response_code: int

    def __init__(self, response_code: _Optional[int] = ...) -> None: ...

class KillMeRequest(_message.Message):
    __slots__ = ("pod_name",)
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    pod_name: str

    def __init__(self, pod_name: _Optional[str] = ...) -> None: ...

class KillMeReply(_message.Message):
    __slots__ = ("response_code",)
    RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    response_code: int

    def __init__(self, response_code: _Optional[int] = ...) -> None: ...
