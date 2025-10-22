from envoy.type.matcher.v3 import value_pb2 as _value_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MetadataMatcher(_message.Message):
    __slots__ = ("filter", "path", "value", "invert")
    class PathSegment(_message.Message):
        __slots__ = ("key",)
        KEY_FIELD_NUMBER: _ClassVar[int]
        key: str
        def __init__(self, key: _Optional[str] = ...) -> None: ...
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    INVERT_FIELD_NUMBER: _ClassVar[int]
    filter: str
    path: _containers.RepeatedCompositeFieldContainer[MetadataMatcher.PathSegment]
    value: _value_pb2.ValueMatcher
    invert: bool
    def __init__(self, filter: _Optional[str] = ..., path: _Optional[_Iterable[_Union[MetadataMatcher.PathSegment, _Mapping]]] = ..., value: _Optional[_Union[_value_pb2.ValueMatcher, _Mapping]] = ..., invert: bool = ...) -> None: ...
