import datetime

from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2_1
from envoy.api.v2.listener import listener_components_pb2 as _listener_components_pb2
from envoy.api.v2.listener import udp_listener_config_pb2 as _udp_listener_config_pb2
from envoy.config.filter.accesslog.v2 import accesslog_pb2 as _accesslog_pb2
from envoy.config.listener.v2 import api_listener_pb2 as _api_listener_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Listener(_message.Message):
    __slots__ = ("name", "address", "filter_chains", "use_original_dst", "per_connection_buffer_limit_bytes", "metadata", "deprecated_v1", "drain_type", "listener_filters", "listener_filters_timeout", "continue_on_listener_filters_timeout", "transparent", "freebind", "socket_options", "tcp_fast_open_queue_length", "traffic_direction", "udp_listener_config", "api_listener", "connection_balance_config", "reuse_port", "access_log")
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
        __slots__ = ("exact_balance",)
        class ExactBalance(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        EXACT_BALANCE_FIELD_NUMBER: _ClassVar[int]
        exact_balance: Listener.ConnectionBalanceConfig.ExactBalance
        def __init__(self, exact_balance: _Optional[_Union[Listener.ConnectionBalanceConfig.ExactBalance, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    FILTER_CHAINS_FIELD_NUMBER: _ClassVar[int]
    USE_ORIGINAL_DST_FIELD_NUMBER: _ClassVar[int]
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
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    name: str
    address: _address_pb2.Address
    filter_chains: _containers.RepeatedCompositeFieldContainer[_listener_components_pb2.FilterChain]
    use_original_dst: _wrappers_pb2.BoolValue
    per_connection_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    metadata: _base_pb2.Metadata
    deprecated_v1: Listener.DeprecatedV1
    drain_type: Listener.DrainType
    listener_filters: _containers.RepeatedCompositeFieldContainer[_listener_components_pb2.ListenerFilter]
    listener_filters_timeout: _duration_pb2.Duration
    continue_on_listener_filters_timeout: bool
    transparent: _wrappers_pb2.BoolValue
    freebind: _wrappers_pb2.BoolValue
    socket_options: _containers.RepeatedCompositeFieldContainer[_socket_option_pb2_1.SocketOption]
    tcp_fast_open_queue_length: _wrappers_pb2.UInt32Value
    traffic_direction: _base_pb2.TrafficDirection
    udp_listener_config: _udp_listener_config_pb2.UdpListenerConfig
    api_listener: _api_listener_pb2.ApiListener
    connection_balance_config: Listener.ConnectionBalanceConfig
    reuse_port: bool
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    def __init__(self, name: _Optional[str] = ..., address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., filter_chains: _Optional[_Iterable[_Union[_listener_components_pb2.FilterChain, _Mapping]]] = ..., use_original_dst: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., per_connection_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., deprecated_v1: _Optional[_Union[Listener.DeprecatedV1, _Mapping]] = ..., drain_type: _Optional[_Union[Listener.DrainType, str]] = ..., listener_filters: _Optional[_Iterable[_Union[_listener_components_pb2.ListenerFilter, _Mapping]]] = ..., listener_filters_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., continue_on_listener_filters_timeout: bool = ..., transparent: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., freebind: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., socket_options: _Optional[_Iterable[_Union[_socket_option_pb2_1.SocketOption, _Mapping]]] = ..., tcp_fast_open_queue_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., traffic_direction: _Optional[_Union[_base_pb2.TrafficDirection, str]] = ..., udp_listener_config: _Optional[_Union[_udp_listener_config_pb2.UdpListenerConfig, _Mapping]] = ..., api_listener: _Optional[_Union[_api_listener_pb2.ApiListener, _Mapping]] = ..., connection_balance_config: _Optional[_Union[Listener.ConnectionBalanceConfig, _Mapping]] = ..., reuse_port: bool = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ...) -> None: ...
