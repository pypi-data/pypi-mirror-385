from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from envoy.type.matcher.v3 import struct_pb2 as _struct_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodeMatcher(_message.Message):
    __slots__ = ("node_id", "node_metadatas")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_METADATAS_FIELD_NUMBER: _ClassVar[int]
    node_id: _string_pb2.StringMatcher
    node_metadatas: _containers.RepeatedCompositeFieldContainer[_struct_pb2.StructMatcher]
    def __init__(self, node_id: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., node_metadatas: _Optional[_Iterable[_Union[_struct_pb2.StructMatcher, _Mapping]]] = ...) -> None: ...
