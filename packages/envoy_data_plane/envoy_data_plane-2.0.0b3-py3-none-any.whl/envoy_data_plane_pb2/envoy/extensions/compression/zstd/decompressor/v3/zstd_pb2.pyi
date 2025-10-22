from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Zstd(_message.Message):
    __slots__ = ("dictionaries", "chunk_size")
    DICTIONARIES_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    dictionaries: _containers.RepeatedCompositeFieldContainer[_base_pb2.DataSource]
    chunk_size: _wrappers_pb2.UInt32Value
    def __init__(self, dictionaries: _Optional[_Iterable[_Union[_base_pb2.DataSource, _Mapping]]] = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
