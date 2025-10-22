from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.route import route_components_pb2 as _route_components_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RouteConfiguration(_message.Message):
    __slots__ = ("name", "routes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    def __init__(self, name: _Optional[str] = ..., routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ...) -> None: ...

class Route(_message.Message):
    __slots__ = ("match", "route")
    MATCH_FIELD_NUMBER: _ClassVar[int]
    ROUTE_FIELD_NUMBER: _ClassVar[int]
    match: RouteMatch
    route: RouteAction
    def __init__(self, match: _Optional[_Union[RouteMatch, _Mapping]] = ..., route: _Optional[_Union[RouteAction, _Mapping]] = ...) -> None: ...

class RouteMatch(_message.Message):
    __slots__ = ("method_name", "service_name", "invert", "headers")
    METHOD_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    INVERT_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    method_name: str
    service_name: str
    invert: bool
    headers: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    def __init__(self, method_name: _Optional[str] = ..., service_name: _Optional[str] = ..., invert: bool = ..., headers: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ...) -> None: ...

class RouteAction(_message.Message):
    __slots__ = ("cluster", "weighted_clusters", "cluster_header", "metadata_match", "rate_limits", "strip_service_name")
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_HEADER_FIELD_NUMBER: _ClassVar[int]
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    STRIP_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    weighted_clusters: WeightedCluster
    cluster_header: str
    metadata_match: _base_pb2.Metadata
    rate_limits: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.RateLimit]
    strip_service_name: bool
    def __init__(self, cluster: _Optional[str] = ..., weighted_clusters: _Optional[_Union[WeightedCluster, _Mapping]] = ..., cluster_header: _Optional[str] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., rate_limits: _Optional[_Iterable[_Union[_route_components_pb2.RateLimit, _Mapping]]] = ..., strip_service_name: bool = ...) -> None: ...

class WeightedCluster(_message.Message):
    __slots__ = ("clusters",)
    class ClusterWeight(_message.Message):
        __slots__ = ("name", "weight", "metadata_match")
        NAME_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
        name: str
        weight: _wrappers_pb2.UInt32Value
        metadata_match: _base_pb2.Metadata
        def __init__(self, name: _Optional[str] = ..., weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedCompositeFieldContainer[WeightedCluster.ClusterWeight]
    def __init__(self, clusters: _Optional[_Iterable[_Union[WeightedCluster.ClusterWeight, _Mapping]]] = ...) -> None: ...
