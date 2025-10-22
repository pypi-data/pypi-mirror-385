from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import health_check_pb2 as _health_check_pb2
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

class Endpoint(_message.Message):
    __slots__ = ("address", "health_check_config", "hostname")
    class HealthCheckConfig(_message.Message):
        __slots__ = ("port_value", "hostname")
        PORT_VALUE_FIELD_NUMBER: _ClassVar[int]
        HOSTNAME_FIELD_NUMBER: _ClassVar[int]
        port_value: int
        hostname: str
        def __init__(self, port_value: _Optional[int] = ..., hostname: _Optional[str] = ...) -> None: ...
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    health_check_config: Endpoint.HealthCheckConfig
    hostname: str
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., health_check_config: _Optional[_Union[Endpoint.HealthCheckConfig, _Mapping]] = ..., hostname: _Optional[str] = ...) -> None: ...

class LbEndpoint(_message.Message):
    __slots__ = ("endpoint", "endpoint_name", "health_status", "metadata", "load_balancing_weight")
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_NAME_FIELD_NUMBER: _ClassVar[int]
    HEALTH_STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LOAD_BALANCING_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    endpoint: Endpoint
    endpoint_name: str
    health_status: _health_check_pb2.HealthStatus
    metadata: _base_pb2.Metadata
    load_balancing_weight: _wrappers_pb2.UInt32Value
    def __init__(self, endpoint: _Optional[_Union[Endpoint, _Mapping]] = ..., endpoint_name: _Optional[str] = ..., health_status: _Optional[_Union[_health_check_pb2.HealthStatus, str]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., load_balancing_weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class LocalityLbEndpoints(_message.Message):
    __slots__ = ("locality", "lb_endpoints", "load_balancing_weight", "priority", "proximity")
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    LB_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    LOAD_BALANCING_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PROXIMITY_FIELD_NUMBER: _ClassVar[int]
    locality: _base_pb2.Locality
    lb_endpoints: _containers.RepeatedCompositeFieldContainer[LbEndpoint]
    load_balancing_weight: _wrappers_pb2.UInt32Value
    priority: int
    proximity: _wrappers_pb2.UInt32Value
    def __init__(self, locality: _Optional[_Union[_base_pb2.Locality, _Mapping]] = ..., lb_endpoints: _Optional[_Iterable[_Union[LbEndpoint, _Mapping]]] = ..., load_balancing_weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., priority: _Optional[int] = ..., proximity: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
