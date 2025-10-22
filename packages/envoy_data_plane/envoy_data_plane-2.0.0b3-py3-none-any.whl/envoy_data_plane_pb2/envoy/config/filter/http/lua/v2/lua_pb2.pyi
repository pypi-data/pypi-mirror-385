from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Lua(_message.Message):
    __slots__ = ("inline_code",)
    INLINE_CODE_FIELD_NUMBER: _ClassVar[int]
    inline_code: str
    def __init__(self, inline_code: _Optional[str] = ...) -> None: ...
