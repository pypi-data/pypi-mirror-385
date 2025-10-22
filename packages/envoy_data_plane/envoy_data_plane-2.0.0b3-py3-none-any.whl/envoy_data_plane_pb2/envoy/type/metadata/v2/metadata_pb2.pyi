from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MetadataKey(_message.Message):
    __slots__ = ("key", "path")
    class PathSegment(_message.Message):
        __slots__ = ("key",)
        KEY_FIELD_NUMBER: _ClassVar[int]
        key: str
        def __init__(self, key: _Optional[str] = ...) -> None: ...
    KEY_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    key: str
    path: _containers.RepeatedCompositeFieldContainer[MetadataKey.PathSegment]
    def __init__(self, key: _Optional[str] = ..., path: _Optional[_Iterable[_Union[MetadataKey.PathSegment, _Mapping]]] = ...) -> None: ...

class MetadataKind(_message.Message):
    __slots__ = ("request", "route", "cluster", "host")
    class Request(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Route(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Cluster(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Host(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    ROUTE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    request: MetadataKind.Request
    route: MetadataKind.Route
    cluster: MetadataKind.Cluster
    host: MetadataKind.Host
    def __init__(self, request: _Optional[_Union[MetadataKind.Request, _Mapping]] = ..., route: _Optional[_Union[MetadataKind.Route, _Mapping]] = ..., cluster: _Optional[_Union[MetadataKind.Cluster, _Mapping]] = ..., host: _Optional[_Union[MetadataKind.Host, _Mapping]] = ...) -> None: ...
