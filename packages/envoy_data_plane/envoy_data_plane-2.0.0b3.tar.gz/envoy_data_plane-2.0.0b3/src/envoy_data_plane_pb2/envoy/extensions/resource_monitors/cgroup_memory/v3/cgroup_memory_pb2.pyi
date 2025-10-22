from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CgroupMemoryConfig(_message.Message):
    __slots__ = ("max_memory_bytes",)
    MAX_MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    max_memory_bytes: int
    def __init__(self, max_memory_bytes: _Optional[int] = ...) -> None: ...
