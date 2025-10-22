from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Metadata(_message.Message):
    __slots__ = ("metadata_namespace", "allow_overwrite", "value", "typed_value")
    METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ALLOW_OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPED_VALUE_FIELD_NUMBER: _ClassVar[int]
    metadata_namespace: str
    allow_overwrite: bool
    value: _struct_pb2.Struct
    typed_value: _any_pb2.Any
    def __init__(self, metadata_namespace: _Optional[str] = ..., allow_overwrite: bool = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("metadata_namespace", "value", "metadata")
    METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata_namespace: str
    value: _struct_pb2.Struct
    metadata: _containers.RepeatedCompositeFieldContainer[Metadata]
    def __init__(self, metadata_namespace: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., metadata: _Optional[_Iterable[_Union[Metadata, _Mapping]]] = ...) -> None: ...
