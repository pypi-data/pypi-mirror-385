from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DynamicModuleConfig(_message.Message):
    __slots__ = ("name", "do_not_close")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DO_NOT_CLOSE_FIELD_NUMBER: _ClassVar[int]
    name: str
    do_not_close: bool
    def __init__(self, name: _Optional[str] = ..., do_not_close: bool = ...) -> None: ...
