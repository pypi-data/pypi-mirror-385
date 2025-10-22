from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import health_check_pb2 as _health_check_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.core.v3 import collection_entry_pb2 as _collection_entry_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Endpoint(_message.Message):
    __slots__ = ("address", "health_check_config", "hostname", "additional_addresses")
    class HealthCheckConfig(_message.Message):
        __slots__ = ("port_value", "hostname", "address", "disable_active_health_check")
        PORT_VALUE_FIELD_NUMBER: _ClassVar[int]
        HOSTNAME_FIELD_NUMBER: _ClassVar[int]
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        DISABLE_ACTIVE_HEALTH_CHECK_FIELD_NUMBER: _ClassVar[int]
        port_value: int
        hostname: str
        address: _address_pb2.Address
        disable_active_health_check: bool
        def __init__(self, port_value: _Optional[int] = ..., hostname: _Optional[str] = ..., address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., disable_active_health_check: bool = ...) -> None: ...
    class AdditionalAddress(_message.Message):
        __slots__ = ("address",)
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        address: _address_pb2.Address
        def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ...) -> None: ...
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    health_check_config: Endpoint.HealthCheckConfig
    hostname: str
    additional_addresses: _containers.RepeatedCompositeFieldContainer[Endpoint.AdditionalAddress]
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., health_check_config: _Optional[_Union[Endpoint.HealthCheckConfig, _Mapping]] = ..., hostname: _Optional[str] = ..., additional_addresses: _Optional[_Iterable[_Union[Endpoint.AdditionalAddress, _Mapping]]] = ...) -> None: ...

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

class LbEndpointCollection(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _collection_entry_pb2.CollectionEntry
    def __init__(self, entries: _Optional[_Union[_collection_entry_pb2.CollectionEntry, _Mapping]] = ...) -> None: ...

class LedsClusterLocalityConfig(_message.Message):
    __slots__ = ("leds_config", "leds_collection_name")
    LEDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LEDS_COLLECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    leds_config: _config_source_pb2.ConfigSource
    leds_collection_name: str
    def __init__(self, leds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., leds_collection_name: _Optional[str] = ...) -> None: ...

class LocalityLbEndpoints(_message.Message):
    __slots__ = ("locality", "metadata", "lb_endpoints", "load_balancer_endpoints", "leds_cluster_locality_config", "load_balancing_weight", "priority", "proximity")
    class LbEndpointList(_message.Message):
        __slots__ = ("lb_endpoints",)
        LB_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
        lb_endpoints: _containers.RepeatedCompositeFieldContainer[LbEndpoint]
        def __init__(self, lb_endpoints: _Optional[_Iterable[_Union[LbEndpoint, _Mapping]]] = ...) -> None: ...
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LB_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    LOAD_BALANCER_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    LEDS_CLUSTER_LOCALITY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LOAD_BALANCING_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PROXIMITY_FIELD_NUMBER: _ClassVar[int]
    locality: _base_pb2.Locality
    metadata: _base_pb2.Metadata
    lb_endpoints: _containers.RepeatedCompositeFieldContainer[LbEndpoint]
    load_balancer_endpoints: LocalityLbEndpoints.LbEndpointList
    leds_cluster_locality_config: LedsClusterLocalityConfig
    load_balancing_weight: _wrappers_pb2.UInt32Value
    priority: int
    proximity: _wrappers_pb2.UInt32Value
    def __init__(self, locality: _Optional[_Union[_base_pb2.Locality, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., lb_endpoints: _Optional[_Iterable[_Union[LbEndpoint, _Mapping]]] = ..., load_balancer_endpoints: _Optional[_Union[LocalityLbEndpoints.LbEndpointList, _Mapping]] = ..., leds_cluster_locality_config: _Optional[_Union[LedsClusterLocalityConfig, _Mapping]] = ..., load_balancing_weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., priority: _Optional[int] = ..., proximity: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
