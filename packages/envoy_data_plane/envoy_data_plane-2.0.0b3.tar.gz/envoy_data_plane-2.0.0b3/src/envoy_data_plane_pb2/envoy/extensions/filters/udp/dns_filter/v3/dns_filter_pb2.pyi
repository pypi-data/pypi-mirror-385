import datetime

from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import resolver_pb2 as _resolver_pb2
from envoy.data.dns.v3 import dns_table_pb2 as _dns_table_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DnsFilterConfig(_message.Message):
    __slots__ = ("stat_prefix", "server_config", "client_config")
    class ServerContextConfig(_message.Message):
        __slots__ = ("inline_dns_table", "external_dns_table")
        INLINE_DNS_TABLE_FIELD_NUMBER: _ClassVar[int]
        EXTERNAL_DNS_TABLE_FIELD_NUMBER: _ClassVar[int]
        inline_dns_table: _dns_table_pb2.DnsTable
        external_dns_table: _base_pb2.DataSource
        def __init__(self, inline_dns_table: _Optional[_Union[_dns_table_pb2.DnsTable, _Mapping]] = ..., external_dns_table: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
    class ClientContextConfig(_message.Message):
        __slots__ = ("resolver_timeout", "upstream_resolvers", "dns_resolution_config", "typed_dns_resolver_config", "max_pending_lookups")
        RESOLVER_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        UPSTREAM_RESOLVERS_FIELD_NUMBER: _ClassVar[int]
        DNS_RESOLUTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
        TYPED_DNS_RESOLVER_CONFIG_FIELD_NUMBER: _ClassVar[int]
        MAX_PENDING_LOOKUPS_FIELD_NUMBER: _ClassVar[int]
        resolver_timeout: _duration_pb2.Duration
        upstream_resolvers: _containers.RepeatedCompositeFieldContainer[_address_pb2.Address]
        dns_resolution_config: _resolver_pb2.DnsResolutionConfig
        typed_dns_resolver_config: _extension_pb2.TypedExtensionConfig
        max_pending_lookups: int
        def __init__(self, resolver_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upstream_resolvers: _Optional[_Iterable[_Union[_address_pb2.Address, _Mapping]]] = ..., dns_resolution_config: _Optional[_Union[_resolver_pb2.DnsResolutionConfig, _Mapping]] = ..., typed_dns_resolver_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., max_pending_lookups: _Optional[int] = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    SERVER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    server_config: DnsFilterConfig.ServerContextConfig
    client_config: DnsFilterConfig.ClientContextConfig
    def __init__(self, stat_prefix: _Optional[str] = ..., server_config: _Optional[_Union[DnsFilterConfig.ServerContextConfig, _Mapping]] = ..., client_config: _Optional[_Union[DnsFilterConfig.ClientContextConfig, _Mapping]] = ...) -> None: ...
