from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Body(_message.Message):
    __slots__ = ("as_bytes", "as_string", "truncated")
    AS_BYTES_FIELD_NUMBER: _ClassVar[int]
    AS_STRING_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    as_bytes: bytes
    as_string: str
    truncated: bool
    def __init__(self, as_bytes: _Optional[bytes] = ..., as_string: _Optional[str] = ..., truncated: bool = ...) -> None: ...
