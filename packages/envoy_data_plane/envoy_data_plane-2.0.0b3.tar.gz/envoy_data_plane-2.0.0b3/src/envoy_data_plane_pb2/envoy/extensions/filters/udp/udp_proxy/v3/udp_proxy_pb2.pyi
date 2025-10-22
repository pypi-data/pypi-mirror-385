import datetime

from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.core.v3 import backoff_pb2 as _backoff_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import udp_socket_config_pb2 as _udp_socket_config_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UdpProxyConfig(_message.Message):
    __slots__ = ("stat_prefix", "cluster", "matcher", "idle_timeout", "use_original_src_ip", "hash_policies", "upstream_socket_config", "use_per_packet_load_balancing", "access_log", "proxy_access_log", "session_filters", "tunneling_config", "access_log_options")
    class HashPolicy(_message.Message):
        __slots__ = ("source_ip", "key")
        SOURCE_IP_FIELD_NUMBER: _ClassVar[int]
        KEY_FIELD_NUMBER: _ClassVar[int]
        source_ip: bool
        key: str
        def __init__(self, source_ip: bool = ..., key: _Optional[str] = ...) -> None: ...
    class SessionFilter(_message.Message):
        __slots__ = ("name", "typed_config", "config_discovery")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        CONFIG_DISCOVERY_FIELD_NUMBER: _ClassVar[int]
        name: str
        typed_config: _any_pb2.Any
        config_discovery: _config_source_pb2.ExtensionConfigSource
        def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., config_discovery: _Optional[_Union[_config_source_pb2.ExtensionConfigSource, _Mapping]] = ...) -> None: ...
    class UdpTunnelingConfig(_message.Message):
        __slots__ = ("proxy_host", "proxy_port", "target_host", "default_target_port", "use_post", "post_path", "retry_options", "headers_to_add", "buffer_options", "propagate_response_headers", "propagate_response_trailers")
        class BufferOptions(_message.Message):
            __slots__ = ("max_buffered_datagrams", "max_buffered_bytes")
            MAX_BUFFERED_DATAGRAMS_FIELD_NUMBER: _ClassVar[int]
            MAX_BUFFERED_BYTES_FIELD_NUMBER: _ClassVar[int]
            max_buffered_datagrams: _wrappers_pb2.UInt32Value
            max_buffered_bytes: _wrappers_pb2.UInt64Value
            def __init__(self, max_buffered_datagrams: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_buffered_bytes: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...
        class RetryOptions(_message.Message):
            __slots__ = ("max_connect_attempts", "backoff_options")
            MAX_CONNECT_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
            BACKOFF_OPTIONS_FIELD_NUMBER: _ClassVar[int]
            max_connect_attempts: _wrappers_pb2.UInt32Value
            backoff_options: _backoff_pb2.BackoffStrategy
            def __init__(self, max_connect_attempts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., backoff_options: _Optional[_Union[_backoff_pb2.BackoffStrategy, _Mapping]] = ...) -> None: ...
        PROXY_HOST_FIELD_NUMBER: _ClassVar[int]
        PROXY_PORT_FIELD_NUMBER: _ClassVar[int]
        TARGET_HOST_FIELD_NUMBER: _ClassVar[int]
        DEFAULT_TARGET_PORT_FIELD_NUMBER: _ClassVar[int]
        USE_POST_FIELD_NUMBER: _ClassVar[int]
        POST_PATH_FIELD_NUMBER: _ClassVar[int]
        RETRY_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        BUFFER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        PROPAGATE_RESPONSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
        PROPAGATE_RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
        proxy_host: str
        proxy_port: _wrappers_pb2.UInt32Value
        target_host: str
        default_target_port: int
        use_post: bool
        post_path: str
        retry_options: UdpProxyConfig.UdpTunnelingConfig.RetryOptions
        headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        buffer_options: UdpProxyConfig.UdpTunnelingConfig.BufferOptions
        propagate_response_headers: bool
        propagate_response_trailers: bool
        def __init__(self, proxy_host: _Optional[str] = ..., proxy_port: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., target_host: _Optional[str] = ..., default_target_port: _Optional[int] = ..., use_post: bool = ..., post_path: _Optional[str] = ..., retry_options: _Optional[_Union[UdpProxyConfig.UdpTunnelingConfig.RetryOptions, _Mapping]] = ..., headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., buffer_options: _Optional[_Union[UdpProxyConfig.UdpTunnelingConfig.BufferOptions, _Mapping]] = ..., propagate_response_headers: bool = ..., propagate_response_trailers: bool = ...) -> None: ...
    class UdpAccessLogOptions(_message.Message):
        __slots__ = ("access_log_flush_interval", "flush_access_log_on_tunnel_connected")
        ACCESS_LOG_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        FLUSH_ACCESS_LOG_ON_TUNNEL_CONNECTED_FIELD_NUMBER: _ClassVar[int]
        access_log_flush_interval: _duration_pb2.Duration
        flush_access_log_on_tunnel_connected: bool
        def __init__(self, access_log_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., flush_access_log_on_tunnel_connected: bool = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    USE_ORIGINAL_SRC_IP_FIELD_NUMBER: _ClassVar[int]
    HASH_POLICIES_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_SOCKET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    USE_PER_PACKET_LOAD_BALANCING_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    PROXY_ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    SESSION_FILTERS_FIELD_NUMBER: _ClassVar[int]
    TUNNELING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    cluster: str
    matcher: _matcher_pb2.Matcher
    idle_timeout: _duration_pb2.Duration
    use_original_src_ip: bool
    hash_policies: _containers.RepeatedCompositeFieldContainer[UdpProxyConfig.HashPolicy]
    upstream_socket_config: _udp_socket_config_pb2.UdpSocketConfig
    use_per_packet_load_balancing: bool
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    proxy_access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    session_filters: _containers.RepeatedCompositeFieldContainer[UdpProxyConfig.SessionFilter]
    tunneling_config: UdpProxyConfig.UdpTunnelingConfig
    access_log_options: UdpProxyConfig.UdpAccessLogOptions
    def __init__(self, stat_prefix: _Optional[str] = ..., cluster: _Optional[str] = ..., matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., use_original_src_ip: bool = ..., hash_policies: _Optional[_Iterable[_Union[UdpProxyConfig.HashPolicy, _Mapping]]] = ..., upstream_socket_config: _Optional[_Union[_udp_socket_config_pb2.UdpSocketConfig, _Mapping]] = ..., use_per_packet_load_balancing: bool = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., proxy_access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., session_filters: _Optional[_Iterable[_Union[UdpProxyConfig.SessionFilter, _Mapping]]] = ..., tunneling_config: _Optional[_Union[UdpProxyConfig.UdpTunnelingConfig, _Mapping]] = ..., access_log_options: _Optional[_Union[UdpProxyConfig.UdpAccessLogOptions, _Mapping]] = ...) -> None: ...
