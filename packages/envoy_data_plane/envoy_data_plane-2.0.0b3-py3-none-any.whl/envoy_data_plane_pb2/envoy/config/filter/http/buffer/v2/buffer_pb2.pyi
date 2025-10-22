from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Buffer(_message.Message):
    __slots__ = ("max_request_bytes",)
    MAX_REQUEST_BYTES_FIELD_NUMBER: _ClassVar[int]
    max_request_bytes: _wrappers_pb2.UInt32Value
    def __init__(self, max_request_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class BufferPerRoute(_message.Message):
    __slots__ = ("disabled", "buffer")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    buffer: Buffer
    def __init__(self, disabled: bool = ..., buffer: _Optional[_Union[Buffer, _Mapping]] = ...) -> None: ...
