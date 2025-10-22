import datetime

from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import socket_option_pb2 as _socket_option_pb2
from envoy.config.listener.v3 import api_listener_pb2 as _api_listener_pb2
from envoy.config.listener.v3 import listener_components_pb2 as _listener_components_pb2
from envoy.config.listener.v3 import udp_listener_config_pb2 as _udp_listener_config_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.core.v3 import collection_entry_pb2 as _collection_entry_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import security_pb2 as _security_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AdditionalAddress(_message.Message):
    __slots__ = ("address", "socket_options")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SOCKET_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    socket_options: _socket_option_pb2.SocketOptionsOverride
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., socket_options: _Optional[_Union[_socket_option_pb2.SocketOptionsOverride, _Mapping]] = ...) -> None: ...

class ListenerCollection(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[_collection_entry_pb2.CollectionEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[_collection_entry_pb2.CollectionEntry, _Mapping]]] = ...) -> None: ...

class Listener(_message.Message):
    __slots__ = ("name", "address", "additional_addresses", "stat_prefix", "filter_chains", "fcds_config", "filter_chain_matcher", "use_original_dst", "default_filter_chain", "per_connection_buffer_limit_bytes", "metadata", "deprecated_v1", "drain_type", "listener_filters", "listener_filters_timeout", "continue_on_listener_filters_timeout", "transparent", "freebind", "socket_options", "tcp_fast_open_queue_length", "traffic_direction", "udp_listener_config", "api_listener", "connection_balance_config", "reuse_port", "enable_reuse_port", "access_log", "tcp_backlog_size", "max_connections_to_accept_per_socket_event", "bind_to_port", "internal_listener", "enable_mptcp", "ignore_global_conn_limit", "bypass_overload_manager")
    class DrainType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[Listener.DrainType]
        MODIFY_ONLY: _ClassVar[Listener.DrainType]
    DEFAULT: Listener.DrainType
    MODIFY_ONLY: Listener.DrainType
    class DeprecatedV1(_message.Message):
        __slots__ = ("bind_to_port",)
        BIND_TO_PORT_FIELD_NUMBER: _ClassVar[int]
        bind_to_port: _wrappers_pb2.BoolValue
        def __init__(self, bind_to_port: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    class ConnectionBalanceConfig(_message.Message):
        __slots__ = ("exact_balance", "extend_balance")
        class ExactBalance(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        EXACT_BALANCE_FIELD_NUMBER: _ClassVar[int]
        EXTEND_BALANCE_FIELD_NUMBER: _ClassVar[int]
        exact_balance: Listener.ConnectionBalanceConfig.ExactBalance
        extend_balance: _extension_pb2.TypedExtensionConfig
        def __init__(self, exact_balance: _Optional[_Union[Listener.ConnectionBalanceConfig.ExactBalance, _Mapping]] = ..., extend_balance: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
    class InternalListenerConfig(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class FcdsConfig(_message.Message):
        __slots__ = ("name", "config_source")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
        name: str
        config_source: _config_source_pb2.ConfigSource
        def __init__(self, name: _Optional[str] = ..., config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    FILTER_CHAINS_FIELD_NUMBER: _ClassVar[int]
    FCDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FILTER_CHAIN_MATCHER_FIELD_NUMBER: _ClassVar[int]
    USE_ORIGINAL_DST_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FILTER_CHAIN_FIELD_NUMBER: _ClassVar[int]
    PER_CONNECTION_BUFFER_LIMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_V1_FIELD_NUMBER: _ClassVar[int]
    DRAIN_TYPE_FIELD_NUMBER: _ClassVar[int]
    LISTENER_FILTERS_FIELD_NUMBER: _ClassVar[int]
    LISTENER_FILTERS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    CONTINUE_ON_LISTENER_FILTERS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    TRANSPARENT_FIELD_NUMBER: _ClassVar[int]
    FREEBIND_FIELD_NUMBER: _ClassVar[int]
    SOCKET_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TCP_FAST_OPEN_QUEUE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TRAFFIC_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    UDP_LISTENER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    API_LISTENER_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_BALANCE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REUSE_PORT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_REUSE_PORT_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    TCP_BACKLOG_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_CONNECTIONS_TO_ACCEPT_PER_SOCKET_EVENT_FIELD_NUMBER: _ClassVar[int]
    BIND_TO_PORT_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_LISTENER_FIELD_NUMBER: _ClassVar[int]
    ENABLE_MPTCP_FIELD_NUMBER: _ClassVar[int]
    IGNORE_GLOBAL_CONN_LIMIT_FIELD_NUMBER: _ClassVar[int]
    BYPASS_OVERLOAD_MANAGER_FIELD_NUMBER: _ClassVar[int]
    name: str
    address: _address_pb2.Address
    additional_addresses: _containers.RepeatedCompositeFieldContainer[AdditionalAddress]
    stat_prefix: str
    filter_chains: _containers.RepeatedCompositeFieldContainer[_listener_components_pb2.FilterChain]
    fcds_config: Listener.FcdsConfig
    filter_chain_matcher: _matcher_pb2.Matcher
    use_original_dst: _wrappers_pb2.BoolValue
    default_filter_chain: _listener_components_pb2.FilterChain
    per_connection_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    metadata: _base_pb2.Metadata
    deprecated_v1: Listener.DeprecatedV1
    drain_type: Listener.DrainType
    listener_filters: _containers.RepeatedCompositeFieldContainer[_listener_components_pb2.ListenerFilter]
    listener_filters_timeout: _duration_pb2.Duration
    continue_on_listener_filters_timeout: bool
    transparent: _wrappers_pb2.BoolValue
    freebind: _wrappers_pb2.BoolValue
    socket_options: _containers.RepeatedCompositeFieldContainer[_socket_option_pb2.SocketOption]
    tcp_fast_open_queue_length: _wrappers_pb2.UInt32Value
    traffic_direction: _base_pb2.TrafficDirection
    udp_listener_config: _udp_listener_config_pb2.UdpListenerConfig
    api_listener: _api_listener_pb2.ApiListener
    connection_balance_config: Listener.ConnectionBalanceConfig
    reuse_port: bool
    enable_reuse_port: _wrappers_pb2.BoolValue
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    tcp_backlog_size: _wrappers_pb2.UInt32Value
    max_connections_to_accept_per_socket_event: _wrappers_pb2.UInt32Value
    bind_to_port: _wrappers_pb2.BoolValue
    internal_listener: Listener.InternalListenerConfig
    enable_mptcp: bool
    ignore_global_conn_limit: bool
    bypass_overload_manager: bool
    def __init__(self, name: _Optional[str] = ..., address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., additional_addresses: _Optional[_Iterable[_Union[AdditionalAddress, _Mapping]]] = ..., stat_prefix: _Optional[str] = ..., filter_chains: _Optional[_Iterable[_Union[_listener_components_pb2.FilterChain, _Mapping]]] = ..., fcds_config: _Optional[_Union[Listener.FcdsConfig, _Mapping]] = ..., filter_chain_matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., use_original_dst: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., default_filter_chain: _Optional[_Union[_listener_components_pb2.FilterChain, _Mapping]] = ..., per_connection_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., deprecated_v1: _Optional[_Union[Listener.DeprecatedV1, _Mapping]] = ..., drain_type: _Optional[_Union[Listener.DrainType, str]] = ..., listener_filters: _Optional[_Iterable[_Union[_listener_components_pb2.ListenerFilter, _Mapping]]] = ..., listener_filters_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., continue_on_listener_filters_timeout: bool = ..., transparent: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., freebind: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., socket_options: _Optional[_Iterable[_Union[_socket_option_pb2.SocketOption, _Mapping]]] = ..., tcp_fast_open_queue_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., traffic_direction: _Optional[_Union[_base_pb2.TrafficDirection, str]] = ..., udp_listener_config: _Optional[_Union[_udp_listener_config_pb2.UdpListenerConfig, _Mapping]] = ..., api_listener: _Optional[_Union[_api_listener_pb2.ApiListener, _Mapping]] = ..., connection_balance_config: _Optional[_Union[Listener.ConnectionBalanceConfig, _Mapping]] = ..., reuse_port: bool = ..., enable_reuse_port: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., tcp_backlog_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_connections_to_accept_per_socket_event: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., bind_to_port: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., internal_listener: _Optional[_Union[Listener.InternalListenerConfig, _Mapping]] = ..., enable_mptcp: bool = ..., ignore_global_conn_limit: bool = ..., bypass_overload_manager: bool = ...) -> None: ...

class ListenerManager(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ValidationListenerManager(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ApiListenerManager(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
