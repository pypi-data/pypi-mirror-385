from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VirtualHost(_message.Message):
    __slots__ = ("name", "hosts", "routes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    HOSTS_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    hosts: _containers.RepeatedScalarFieldContainer[str]
    routes: _matcher_pb2.Matcher
    def __init__(self, name: _Optional[str] = ..., hosts: _Optional[_Iterable[str]] = ..., routes: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ...) -> None: ...

class RouteConfiguration(_message.Message):
    __slots__ = ("name", "routes", "virtual_hosts")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_HOSTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    routes: _matcher_pb2.Matcher
    virtual_hosts: _containers.RepeatedCompositeFieldContainer[VirtualHost]
    def __init__(self, name: _Optional[str] = ..., routes: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., virtual_hosts: _Optional[_Iterable[_Union[VirtualHost, _Mapping]]] = ...) -> None: ...
