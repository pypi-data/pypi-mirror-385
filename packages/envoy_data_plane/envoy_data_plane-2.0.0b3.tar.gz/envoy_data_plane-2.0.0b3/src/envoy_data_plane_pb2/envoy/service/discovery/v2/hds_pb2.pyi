import datetime

from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import health_check_pb2 as _health_check_pb2
from envoy.api.v2.endpoint import endpoint_components_pb2 as _endpoint_components_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Capability(_message.Message):
    __slots__ = ("health_check_protocols",)
    class Protocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HTTP: _ClassVar[Capability.Protocol]
        TCP: _ClassVar[Capability.Protocol]
        REDIS: _ClassVar[Capability.Protocol]
    HTTP: Capability.Protocol
    TCP: Capability.Protocol
    REDIS: Capability.Protocol
    HEALTH_CHECK_PROTOCOLS_FIELD_NUMBER: _ClassVar[int]
    health_check_protocols: _containers.RepeatedScalarFieldContainer[Capability.Protocol]
    def __init__(self, health_check_protocols: _Optional[_Iterable[_Union[Capability.Protocol, str]]] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ("node", "capability")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CAPABILITY_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    capability: Capability
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., capability: _Optional[_Union[Capability, _Mapping]] = ...) -> None: ...

class EndpointHealth(_message.Message):
    __slots__ = ("endpoint", "health_status")
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    HEALTH_STATUS_FIELD_NUMBER: _ClassVar[int]
    endpoint: _endpoint_components_pb2.Endpoint
    health_status: _health_check_pb2.HealthStatus
    def __init__(self, endpoint: _Optional[_Union[_endpoint_components_pb2.Endpoint, _Mapping]] = ..., health_status: _Optional[_Union[_health_check_pb2.HealthStatus, str]] = ...) -> None: ...

class EndpointHealthResponse(_message.Message):
    __slots__ = ("endpoints_health",)
    ENDPOINTS_HEALTH_FIELD_NUMBER: _ClassVar[int]
    endpoints_health: _containers.RepeatedCompositeFieldContainer[EndpointHealth]
    def __init__(self, endpoints_health: _Optional[_Iterable[_Union[EndpointHealth, _Mapping]]] = ...) -> None: ...

class HealthCheckRequestOrEndpointHealthResponse(_message.Message):
    __slots__ = ("health_check_request", "endpoint_health_response")
    HEALTH_CHECK_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_HEALTH_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    health_check_request: HealthCheckRequest
    endpoint_health_response: EndpointHealthResponse
    def __init__(self, health_check_request: _Optional[_Union[HealthCheckRequest, _Mapping]] = ..., endpoint_health_response: _Optional[_Union[EndpointHealthResponse, _Mapping]] = ...) -> None: ...

class LocalityEndpoints(_message.Message):
    __slots__ = ("locality", "endpoints")
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    locality: _base_pb2.Locality
    endpoints: _containers.RepeatedCompositeFieldContainer[_endpoint_components_pb2.Endpoint]
    def __init__(self, locality: _Optional[_Union[_base_pb2.Locality, _Mapping]] = ..., endpoints: _Optional[_Iterable[_Union[_endpoint_components_pb2.Endpoint, _Mapping]]] = ...) -> None: ...

class ClusterHealthCheck(_message.Message):
    __slots__ = ("cluster_name", "health_checks", "locality_endpoints")
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECKS_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    cluster_name: str
    health_checks: _containers.RepeatedCompositeFieldContainer[_health_check_pb2.HealthCheck]
    locality_endpoints: _containers.RepeatedCompositeFieldContainer[LocalityEndpoints]
    def __init__(self, cluster_name: _Optional[str] = ..., health_checks: _Optional[_Iterable[_Union[_health_check_pb2.HealthCheck, _Mapping]]] = ..., locality_endpoints: _Optional[_Iterable[_Union[LocalityEndpoints, _Mapping]]] = ...) -> None: ...

class HealthCheckSpecifier(_message.Message):
    __slots__ = ("cluster_health_checks", "interval")
    CLUSTER_HEALTH_CHECKS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    cluster_health_checks: _containers.RepeatedCompositeFieldContainer[ClusterHealthCheck]
    interval: _duration_pb2.Duration
    def __init__(self, cluster_health_checks: _Optional[_Iterable[_Union[ClusterHealthCheck, _Mapping]]] = ..., interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
