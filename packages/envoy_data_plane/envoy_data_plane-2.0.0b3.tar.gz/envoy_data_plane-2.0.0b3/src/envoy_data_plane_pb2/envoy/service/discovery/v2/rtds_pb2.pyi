from envoy.api.v2 import discovery_pb2 as _discovery_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from envoy.annotations import resource_pb2 as _resource_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RtdsDummy(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Runtime(_message.Message):
    __slots__ = ("name", "layer")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LAYER_FIELD_NUMBER: _ClassVar[int]
    name: str
    layer: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., layer: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
