import datetime

from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.type.v3 import range_pb2 as _range_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Filter(_message.Message):
    __slots__ = ("name", "typed_config", "config_discovery")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DISCOVERY_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    config_discovery: _config_source_pb2.ExtensionConfigSource
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., config_discovery: _Optional[_Union[_config_source_pb2.ExtensionConfigSource, _Mapping]] = ...) -> None: ...

class FilterChainMatch(_message.Message):
    __slots__ = ("destination_port", "prefix_ranges", "address_suffix", "suffix_len", "direct_source_prefix_ranges", "source_type", "source_prefix_ranges", "source_ports", "server_names", "transport_protocol", "application_protocols")
    class ConnectionSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ANY: _ClassVar[FilterChainMatch.ConnectionSourceType]
        SAME_IP_OR_LOOPBACK: _ClassVar[FilterChainMatch.ConnectionSourceType]
        EXTERNAL: _ClassVar[FilterChainMatch.ConnectionSourceType]
    ANY: FilterChainMatch.ConnectionSourceType
    SAME_IP_OR_LOOPBACK: FilterChainMatch.ConnectionSourceType
    EXTERNAL: FilterChainMatch.ConnectionSourceType
    DESTINATION_PORT_FIELD_NUMBER: _ClassVar[int]
    PREFIX_RANGES_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_SUFFIX_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_LEN_FIELD_NUMBER: _ClassVar[int]
    DIRECT_SOURCE_PREFIX_RANGES_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_PREFIX_RANGES_FIELD_NUMBER: _ClassVar[int]
    SOURCE_PORTS_FIELD_NUMBER: _ClassVar[int]
    SERVER_NAMES_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_PROTOCOLS_FIELD_NUMBER: _ClassVar[int]
    destination_port: _wrappers_pb2.UInt32Value
    prefix_ranges: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    address_suffix: str
    suffix_len: _wrappers_pb2.UInt32Value
    direct_source_prefix_ranges: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    source_type: FilterChainMatch.ConnectionSourceType
    source_prefix_ranges: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    source_ports: _containers.RepeatedScalarFieldContainer[int]
    server_names: _containers.RepeatedScalarFieldContainer[str]
    transport_protocol: str
    application_protocols: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, destination_port: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., prefix_ranges: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., address_suffix: _Optional[str] = ..., suffix_len: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., direct_source_prefix_ranges: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., source_type: _Optional[_Union[FilterChainMatch.ConnectionSourceType, str]] = ..., source_prefix_ranges: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., source_ports: _Optional[_Iterable[int]] = ..., server_names: _Optional[_Iterable[str]] = ..., transport_protocol: _Optional[str] = ..., application_protocols: _Optional[_Iterable[str]] = ...) -> None: ...

class FilterChain(_message.Message):
    __slots__ = ("filter_chain_match", "filters", "use_proxy_proto", "metadata", "transport_socket", "transport_socket_connect_timeout", "name")
    FILTER_CHAIN_MATCH_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    USE_PROXY_PROTO_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_SOCKET_CONNECT_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    filter_chain_match: FilterChainMatch
    filters: _containers.RepeatedCompositeFieldContainer[Filter]
    use_proxy_proto: _wrappers_pb2.BoolValue
    metadata: _base_pb2.Metadata
    transport_socket: _base_pb2.TransportSocket
    transport_socket_connect_timeout: _duration_pb2.Duration
    name: str
    def __init__(self, filter_chain_match: _Optional[_Union[FilterChainMatch, _Mapping]] = ..., filters: _Optional[_Iterable[_Union[Filter, _Mapping]]] = ..., use_proxy_proto: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ..., transport_socket_connect_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...

class ListenerFilterChainMatchPredicate(_message.Message):
    __slots__ = ("or_match", "and_match", "not_match", "any_match", "destination_port_range")
    class MatchSet(_message.Message):
        __slots__ = ("rules",)
        RULES_FIELD_NUMBER: _ClassVar[int]
        rules: _containers.RepeatedCompositeFieldContainer[ListenerFilterChainMatchPredicate]
        def __init__(self, rules: _Optional[_Iterable[_Union[ListenerFilterChainMatchPredicate, _Mapping]]] = ...) -> None: ...
    OR_MATCH_FIELD_NUMBER: _ClassVar[int]
    AND_MATCH_FIELD_NUMBER: _ClassVar[int]
    NOT_MATCH_FIELD_NUMBER: _ClassVar[int]
    ANY_MATCH_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PORT_RANGE_FIELD_NUMBER: _ClassVar[int]
    or_match: ListenerFilterChainMatchPredicate.MatchSet
    and_match: ListenerFilterChainMatchPredicate.MatchSet
    not_match: ListenerFilterChainMatchPredicate
    any_match: bool
    destination_port_range: _range_pb2.Int32Range
    def __init__(self, or_match: _Optional[_Union[ListenerFilterChainMatchPredicate.MatchSet, _Mapping]] = ..., and_match: _Optional[_Union[ListenerFilterChainMatchPredicate.MatchSet, _Mapping]] = ..., not_match: _Optional[_Union[ListenerFilterChainMatchPredicate, _Mapping]] = ..., any_match: bool = ..., destination_port_range: _Optional[_Union[_range_pb2.Int32Range, _Mapping]] = ...) -> None: ...

class ListenerFilter(_message.Message):
    __slots__ = ("name", "typed_config", "config_discovery", "filter_disabled")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DISCOVERY_FIELD_NUMBER: _ClassVar[int]
    FILTER_DISABLED_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    config_discovery: _config_source_pb2.ExtensionConfigSource
    filter_disabled: ListenerFilterChainMatchPredicate
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., config_discovery: _Optional[_Union[_config_source_pb2.ExtensionConfigSource, _Mapping]] = ..., filter_disabled: _Optional[_Union[ListenerFilterChainMatchPredicate, _Mapping]] = ...) -> None: ...
