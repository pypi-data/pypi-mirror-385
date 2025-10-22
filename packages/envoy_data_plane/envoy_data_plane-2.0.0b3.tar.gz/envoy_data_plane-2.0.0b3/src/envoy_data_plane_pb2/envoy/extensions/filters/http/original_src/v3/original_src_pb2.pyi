from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OriginalSrc(_message.Message):
    __slots__ = ("mark",)
    MARK_FIELD_NUMBER: _ClassVar[int]
    mark: int
    def __init__(self, mark: _Optional[int] = ...) -> None: ...
