import datetime

from envoy.config.cluster.v3 import cluster_pb2 as _cluster_pb2
from envoy.config.common.key_value.v3 import config_pb2 as _config_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import resolver_pb2 as _resolver_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
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

class DnsCacheCircuitBreakers(_message.Message):
    __slots__ = ("max_pending_requests",)
    MAX_PENDING_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    max_pending_requests: _wrappers_pb2.UInt32Value
    def __init__(self, max_pending_requests: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class DnsCacheConfig(_message.Message):
    __slots__ = ("name", "dns_lookup_family", "dns_refresh_rate", "dns_min_refresh_rate", "host_ttl", "max_hosts", "disable_dns_refresh_on_failure", "dns_failure_refresh_rate", "dns_cache_circuit_breaker", "use_tcp_for_dns_lookups", "dns_resolution_config", "typed_dns_resolver_config", "preresolve_hostnames", "dns_query_timeout", "key_value_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DNS_LOOKUP_FAMILY_FIELD_NUMBER: _ClassVar[int]
    DNS_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    DNS_MIN_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    HOST_TTL_FIELD_NUMBER: _ClassVar[int]
    MAX_HOSTS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_DNS_REFRESH_ON_FAILURE_FIELD_NUMBER: _ClassVar[int]
    DNS_FAILURE_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    DNS_CACHE_CIRCUIT_BREAKER_FIELD_NUMBER: _ClassVar[int]
    USE_TCP_FOR_DNS_LOOKUPS_FIELD_NUMBER: _ClassVar[int]
    DNS_RESOLUTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_DNS_RESOLVER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PRERESOLVE_HOSTNAMES_FIELD_NUMBER: _ClassVar[int]
    DNS_QUERY_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    KEY_VALUE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    dns_lookup_family: _cluster_pb2.Cluster.DnsLookupFamily
    dns_refresh_rate: _duration_pb2.Duration
    dns_min_refresh_rate: _duration_pb2.Duration
    host_ttl: _duration_pb2.Duration
    max_hosts: _wrappers_pb2.UInt32Value
    disable_dns_refresh_on_failure: bool
    dns_failure_refresh_rate: _cluster_pb2.Cluster.RefreshRate
    dns_cache_circuit_breaker: DnsCacheCircuitBreakers
    use_tcp_for_dns_lookups: bool
    dns_resolution_config: _resolver_pb2.DnsResolutionConfig
    typed_dns_resolver_config: _extension_pb2.TypedExtensionConfig
    preresolve_hostnames: _containers.RepeatedCompositeFieldContainer[_address_pb2.SocketAddress]
    dns_query_timeout: _duration_pb2.Duration
    key_value_config: _config_pb2.KeyValueStoreConfig
    def __init__(self, name: _Optional[str] = ..., dns_lookup_family: _Optional[_Union[_cluster_pb2.Cluster.DnsLookupFamily, str]] = ..., dns_refresh_rate: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., dns_min_refresh_rate: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., host_ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_hosts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., disable_dns_refresh_on_failure: bool = ..., dns_failure_refresh_rate: _Optional[_Union[_cluster_pb2.Cluster.RefreshRate, _Mapping]] = ..., dns_cache_circuit_breaker: _Optional[_Union[DnsCacheCircuitBreakers, _Mapping]] = ..., use_tcp_for_dns_lookups: bool = ..., dns_resolution_config: _Optional[_Union[_resolver_pb2.DnsResolutionConfig, _Mapping]] = ..., typed_dns_resolver_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., preresolve_hostnames: _Optional[_Iterable[_Union[_address_pb2.SocketAddress, _Mapping]]] = ..., dns_query_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., key_value_config: _Optional[_Union[_config_pb2.KeyValueStoreConfig, _Mapping]] = ...) -> None: ...
