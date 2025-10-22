from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FixedHeapConfig(_message.Message):
    __slots__ = ("max_heap_size_bytes",)
    MAX_HEAP_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    max_heap_size_bytes: int
    def __init__(self, max_heap_size_bytes: _Optional[int] = ...) -> None: ...
