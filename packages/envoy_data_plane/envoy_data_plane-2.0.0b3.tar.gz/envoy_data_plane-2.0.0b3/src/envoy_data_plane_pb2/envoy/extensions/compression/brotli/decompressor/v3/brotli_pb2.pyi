from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Brotli(_message.Message):
    __slots__ = ("disable_ring_buffer_reallocation", "chunk_size")
    DISABLE_RING_BUFFER_REALLOCATION_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    disable_ring_buffer_reallocation: bool
    chunk_size: _wrappers_pb2.UInt32Value
    def __init__(self, disable_ring_buffer_reallocation: bool = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
