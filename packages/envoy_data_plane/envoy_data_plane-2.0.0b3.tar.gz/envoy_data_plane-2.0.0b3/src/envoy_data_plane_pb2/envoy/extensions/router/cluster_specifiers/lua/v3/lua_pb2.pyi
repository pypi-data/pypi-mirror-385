from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LuaConfig(_message.Message):
    __slots__ = ("source_code", "default_cluster")
    SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    source_code: _base_pb2.DataSource
    default_cluster: str
    def __init__(self, source_code: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., default_cluster: _Optional[str] = ...) -> None: ...
