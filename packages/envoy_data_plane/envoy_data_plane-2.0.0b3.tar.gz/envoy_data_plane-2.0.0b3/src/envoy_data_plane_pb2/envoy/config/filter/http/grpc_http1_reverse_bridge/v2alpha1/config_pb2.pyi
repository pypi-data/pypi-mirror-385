from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("content_type", "withhold_grpc_frames")
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    WITHHOLD_GRPC_FRAMES_FIELD_NUMBER: _ClassVar[int]
    content_type: str
    withhold_grpc_frames: bool
    def __init__(self, content_type: _Optional[str] = ..., withhold_grpc_frames: bool = ...) -> None: ...

class FilterConfigPerRoute(_message.Message):
    __slots__ = ("disabled",)
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    def __init__(self, disabled: bool = ...) -> None: ...
