from envoy.config.route.v3 import route_pb2 as _route_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ScopedRouteConfiguration(_message.Message):
    __slots__ = ("on_demand", "name", "route_configuration_name", "route_configuration", "key")
    class Key(_message.Message):
        __slots__ = ("fragments",)
        class Fragment(_message.Message):
            __slots__ = ("string_key",)
            STRING_KEY_FIELD_NUMBER: _ClassVar[int]
            string_key: str
            def __init__(self, string_key: _Optional[str] = ...) -> None: ...
        FRAGMENTS_FIELD_NUMBER: _ClassVar[int]
        fragments: _containers.RepeatedCompositeFieldContainer[ScopedRouteConfiguration.Key.Fragment]
        def __init__(self, fragments: _Optional[_Iterable[_Union[ScopedRouteConfiguration.Key.Fragment, _Mapping]]] = ...) -> None: ...
    ON_DEMAND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIGURATION_NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    on_demand: bool
    name: str
    route_configuration_name: str
    route_configuration: _route_pb2.RouteConfiguration
    key: ScopedRouteConfiguration.Key
    def __init__(self, on_demand: bool = ..., name: _Optional[str] = ..., route_configuration_name: _Optional[str] = ..., route_configuration: _Optional[_Union[_route_pb2.RouteConfiguration, _Mapping]] = ..., key: _Optional[_Union[ScopedRouteConfiguration.Key, _Mapping]] = ...) -> None: ...
