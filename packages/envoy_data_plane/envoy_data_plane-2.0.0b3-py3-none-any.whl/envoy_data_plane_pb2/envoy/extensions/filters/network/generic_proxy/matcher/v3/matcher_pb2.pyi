from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServiceMatchInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HostMatchInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PathMatchInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MethodMatchInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PropertyMatchInput(_message.Message):
    __slots__ = ("property_name",)
    PROPERTY_NAME_FIELD_NUMBER: _ClassVar[int]
    property_name: str
    def __init__(self, property_name: _Optional[str] = ...) -> None: ...

class RequestMatchInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class KeyValueMatchEntry(_message.Message):
    __slots__ = ("name", "string_match")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    name: str
    string_match: _string_pb2.StringMatcher
    def __init__(self, name: _Optional[str] = ..., string_match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ...) -> None: ...

class RequestMatcher(_message.Message):
    __slots__ = ("host", "path", "method", "properties")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    host: _string_pb2.StringMatcher
    path: _string_pb2.StringMatcher
    method: _string_pb2.StringMatcher
    properties: _containers.RepeatedCompositeFieldContainer[KeyValueMatchEntry]
    def __init__(self, host: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., path: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., method: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., properties: _Optional[_Iterable[_Union[KeyValueMatchEntry, _Mapping]]] = ...) -> None: ...
