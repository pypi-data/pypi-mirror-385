from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Gzip(_message.Message):
    __slots__ = ("window_bits", "chunk_size", "max_inflate_ratio")
    WINDOW_BITS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_INFLATE_RATIO_FIELD_NUMBER: _ClassVar[int]
    window_bits: _wrappers_pb2.UInt32Value
    chunk_size: _wrappers_pb2.UInt32Value
    max_inflate_ratio: _wrappers_pb2.UInt32Value
    def __init__(self, window_bits: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_inflate_ratio: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
