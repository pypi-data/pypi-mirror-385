from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from envoy.type.v3 import range_pb2 as _range_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RouteConfiguration(_message.Message):
    __slots__ = ("name", "interface", "group", "version", "routes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    interface: str
    group: str
    version: str
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    def __init__(self, name: _Optional[str] = ..., interface: _Optional[str] = ..., group: _Optional[str] = ..., version: _Optional[str] = ..., routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ...) -> None: ...

class Route(_message.Message):
    __slots__ = ("match", "route")
    MATCH_FIELD_NUMBER: _ClassVar[int]
    ROUTE_FIELD_NUMBER: _ClassVar[int]
    match: RouteMatch
    route: RouteAction
    def __init__(self, match: _Optional[_Union[RouteMatch, _Mapping]] = ..., route: _Optional[_Union[RouteAction, _Mapping]] = ...) -> None: ...

class RouteMatch(_message.Message):
    __slots__ = ("method", "headers")
    METHOD_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    method: MethodMatch
    headers: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    def __init__(self, method: _Optional[_Union[MethodMatch, _Mapping]] = ..., headers: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ...) -> None: ...

class RouteAction(_message.Message):
    __slots__ = ("cluster", "weighted_clusters", "metadata_match")
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    weighted_clusters: _route_components_pb2.WeightedCluster
    metadata_match: _base_pb2.Metadata
    def __init__(self, cluster: _Optional[str] = ..., weighted_clusters: _Optional[_Union[_route_components_pb2.WeightedCluster, _Mapping]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...

class MethodMatch(_message.Message):
    __slots__ = ("name", "params_match")
    class ParameterMatchSpecifier(_message.Message):
        __slots__ = ("exact_match", "range_match")
        EXACT_MATCH_FIELD_NUMBER: _ClassVar[int]
        RANGE_MATCH_FIELD_NUMBER: _ClassVar[int]
        exact_match: str
        range_match: _range_pb2.Int64Range
        def __init__(self, exact_match: _Optional[str] = ..., range_match: _Optional[_Union[_range_pb2.Int64Range, _Mapping]] = ...) -> None: ...
    class ParamsMatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: MethodMatch.ParameterMatchSpecifier
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[MethodMatch.ParameterMatchSpecifier, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_MATCH_FIELD_NUMBER: _ClassVar[int]
    name: _string_pb2.StringMatcher
    params_match: _containers.MessageMap[int, MethodMatch.ParameterMatchSpecifier]
    def __init__(self, name: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., params_match: _Optional[_Mapping[int, MethodMatch.ParameterMatchSpecifier]] = ...) -> None: ...

class MultipleRouteConfiguration(_message.Message):
    __slots__ = ("name", "route_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    route_config: _containers.RepeatedCompositeFieldContainer[RouteConfiguration]
    def __init__(self, name: _Optional[str] = ..., route_config: _Optional[_Iterable[_Union[RouteConfiguration, _Mapping]]] = ...) -> None: ...
