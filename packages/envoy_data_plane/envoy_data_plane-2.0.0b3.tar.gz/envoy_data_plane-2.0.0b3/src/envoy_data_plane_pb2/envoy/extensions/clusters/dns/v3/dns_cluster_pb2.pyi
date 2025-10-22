import datetime

from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.extensions.clusters.common.dns.v3 import dns_pb2 as _dns_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DnsCluster(_message.Message):
    __slots__ = ("dns_refresh_rate", "dns_failure_refresh_rate", "respect_dns_ttl", "dns_jitter", "typed_dns_resolver_config", "dns_lookup_family", "all_addresses_in_single_endpoint")
    class RefreshRate(_message.Message):
        __slots__ = ("base_interval", "max_interval")
        BASE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        MAX_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        base_interval: _duration_pb2.Duration
        max_interval: _duration_pb2.Duration
        def __init__(self, base_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    DNS_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    DNS_FAILURE_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    RESPECT_DNS_TTL_FIELD_NUMBER: _ClassVar[int]
    DNS_JITTER_FIELD_NUMBER: _ClassVar[int]
    TYPED_DNS_RESOLVER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DNS_LOOKUP_FAMILY_FIELD_NUMBER: _ClassVar[int]
    ALL_ADDRESSES_IN_SINGLE_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    dns_refresh_rate: _duration_pb2.Duration
    dns_failure_refresh_rate: DnsCluster.RefreshRate
    respect_dns_ttl: bool
    dns_jitter: _duration_pb2.Duration
    typed_dns_resolver_config: _extension_pb2.TypedExtensionConfig
    dns_lookup_family: _dns_pb2.DnsLookupFamily
    all_addresses_in_single_endpoint: bool
    def __init__(self, dns_refresh_rate: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., dns_failure_refresh_rate: _Optional[_Union[DnsCluster.RefreshRate, _Mapping]] = ..., respect_dns_ttl: bool = ..., dns_jitter: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., typed_dns_resolver_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., dns_lookup_family: _Optional[_Union[_dns_pb2.DnsLookupFamily, str]] = ..., all_addresses_in_single_endpoint: bool = ...) -> None: ...
