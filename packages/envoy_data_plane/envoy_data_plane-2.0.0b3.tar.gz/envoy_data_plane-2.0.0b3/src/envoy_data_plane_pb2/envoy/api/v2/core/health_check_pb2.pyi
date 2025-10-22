import datetime

from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import event_service_config_pb2 as _event_service_config_pb2
from envoy.type import http_pb2 as _http_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from envoy.type import range_pb2 as _range_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
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

class HealthStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[HealthStatus]
    HEALTHY: _ClassVar[HealthStatus]
    UNHEALTHY: _ClassVar[HealthStatus]
    DRAINING: _ClassVar[HealthStatus]
    TIMEOUT: _ClassVar[HealthStatus]
    DEGRADED: _ClassVar[HealthStatus]
UNKNOWN: HealthStatus
HEALTHY: HealthStatus
UNHEALTHY: HealthStatus
DRAINING: HealthStatus
TIMEOUT: HealthStatus
DEGRADED: HealthStatus

class HealthCheck(_message.Message):
    __slots__ = ("timeout", "interval", "initial_jitter", "interval_jitter", "interval_jitter_percent", "unhealthy_threshold", "healthy_threshold", "alt_port", "reuse_connection", "http_health_check", "tcp_health_check", "grpc_health_check", "custom_health_check", "no_traffic_interval", "unhealthy_interval", "unhealthy_edge_interval", "healthy_edge_interval", "event_log_path", "event_service", "always_log_health_check_failures", "tls_options")
    class Payload(_message.Message):
        __slots__ = ("text", "binary")
        TEXT_FIELD_NUMBER: _ClassVar[int]
        BINARY_FIELD_NUMBER: _ClassVar[int]
        text: str
        binary: bytes
        def __init__(self, text: _Optional[str] = ..., binary: _Optional[bytes] = ...) -> None: ...
    class HttpHealthCheck(_message.Message):
        __slots__ = ("host", "path", "send", "receive", "service_name", "request_headers_to_add", "request_headers_to_remove", "use_http2", "expected_statuses", "codec_client_type", "service_name_matcher")
        HOST_FIELD_NUMBER: _ClassVar[int]
        PATH_FIELD_NUMBER: _ClassVar[int]
        SEND_FIELD_NUMBER: _ClassVar[int]
        RECEIVE_FIELD_NUMBER: _ClassVar[int]
        SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
        USE_HTTP2_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_STATUSES_FIELD_NUMBER: _ClassVar[int]
        CODEC_CLIENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        SERVICE_NAME_MATCHER_FIELD_NUMBER: _ClassVar[int]
        host: str
        path: str
        send: HealthCheck.Payload
        receive: HealthCheck.Payload
        service_name: str
        request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
        use_http2: bool
        expected_statuses: _containers.RepeatedCompositeFieldContainer[_range_pb2.Int64Range]
        codec_client_type: _http_pb2.CodecClientType
        service_name_matcher: _string_pb2.StringMatcher
        def __init__(self, host: _Optional[str] = ..., path: _Optional[str] = ..., send: _Optional[_Union[HealthCheck.Payload, _Mapping]] = ..., receive: _Optional[_Union[HealthCheck.Payload, _Mapping]] = ..., service_name: _Optional[str] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., use_http2: bool = ..., expected_statuses: _Optional[_Iterable[_Union[_range_pb2.Int64Range, _Mapping]]] = ..., codec_client_type: _Optional[_Union[_http_pb2.CodecClientType, str]] = ..., service_name_matcher: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ...) -> None: ...
    class TcpHealthCheck(_message.Message):
        __slots__ = ("send", "receive")
        SEND_FIELD_NUMBER: _ClassVar[int]
        RECEIVE_FIELD_NUMBER: _ClassVar[int]
        send: HealthCheck.Payload
        receive: _containers.RepeatedCompositeFieldContainer[HealthCheck.Payload]
        def __init__(self, send: _Optional[_Union[HealthCheck.Payload, _Mapping]] = ..., receive: _Optional[_Iterable[_Union[HealthCheck.Payload, _Mapping]]] = ...) -> None: ...
    class RedisHealthCheck(_message.Message):
        __slots__ = ("key",)
        KEY_FIELD_NUMBER: _ClassVar[int]
        key: str
        def __init__(self, key: _Optional[str] = ...) -> None: ...
    class GrpcHealthCheck(_message.Message):
        __slots__ = ("service_name", "authority")
        SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        AUTHORITY_FIELD_NUMBER: _ClassVar[int]
        service_name: str
        authority: str
        def __init__(self, service_name: _Optional[str] = ..., authority: _Optional[str] = ...) -> None: ...
    class CustomHealthCheck(_message.Message):
        __slots__ = ("name", "config", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CONFIG_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        config: _struct_pb2.Struct
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class TlsOptions(_message.Message):
        __slots__ = ("alpn_protocols",)
        ALPN_PROTOCOLS_FIELD_NUMBER: _ClassVar[int]
        alpn_protocols: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, alpn_protocols: _Optional[_Iterable[str]] = ...) -> None: ...
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    INITIAL_JITTER_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_JITTER_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_JITTER_PERCENT_FIELD_NUMBER: _ClassVar[int]
    UNHEALTHY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    ALT_PORT_FIELD_NUMBER: _ClassVar[int]
    REUSE_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    HTTP_HEALTH_CHECK_FIELD_NUMBER: _ClassVar[int]
    TCP_HEALTH_CHECK_FIELD_NUMBER: _ClassVar[int]
    GRPC_HEALTH_CHECK_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_HEALTH_CHECK_FIELD_NUMBER: _ClassVar[int]
    NO_TRAFFIC_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    UNHEALTHY_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    UNHEALTHY_EDGE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_EDGE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    EVENT_LOG_PATH_FIELD_NUMBER: _ClassVar[int]
    EVENT_SERVICE_FIELD_NUMBER: _ClassVar[int]
    ALWAYS_LOG_HEALTH_CHECK_FAILURES_FIELD_NUMBER: _ClassVar[int]
    TLS_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    timeout: _duration_pb2.Duration
    interval: _duration_pb2.Duration
    initial_jitter: _duration_pb2.Duration
    interval_jitter: _duration_pb2.Duration
    interval_jitter_percent: int
    unhealthy_threshold: _wrappers_pb2.UInt32Value
    healthy_threshold: _wrappers_pb2.UInt32Value
    alt_port: _wrappers_pb2.UInt32Value
    reuse_connection: _wrappers_pb2.BoolValue
    http_health_check: HealthCheck.HttpHealthCheck
    tcp_health_check: HealthCheck.TcpHealthCheck
    grpc_health_check: HealthCheck.GrpcHealthCheck
    custom_health_check: HealthCheck.CustomHealthCheck
    no_traffic_interval: _duration_pb2.Duration
    unhealthy_interval: _duration_pb2.Duration
    unhealthy_edge_interval: _duration_pb2.Duration
    healthy_edge_interval: _duration_pb2.Duration
    event_log_path: str
    event_service: _event_service_config_pb2.EventServiceConfig
    always_log_health_check_failures: bool
    tls_options: HealthCheck.TlsOptions
    def __init__(self, timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., initial_jitter: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., interval_jitter: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., interval_jitter_percent: _Optional[int] = ..., unhealthy_threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., healthy_threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., alt_port: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., reuse_connection: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., http_health_check: _Optional[_Union[HealthCheck.HttpHealthCheck, _Mapping]] = ..., tcp_health_check: _Optional[_Union[HealthCheck.TcpHealthCheck, _Mapping]] = ..., grpc_health_check: _Optional[_Union[HealthCheck.GrpcHealthCheck, _Mapping]] = ..., custom_health_check: _Optional[_Union[HealthCheck.CustomHealthCheck, _Mapping]] = ..., no_traffic_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., unhealthy_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., unhealthy_edge_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., healthy_edge_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., event_log_path: _Optional[str] = ..., event_service: _Optional[_Union[_event_service_config_pb2.EventServiceConfig, _Mapping]] = ..., always_log_health_check_failures: bool = ..., tls_options: _Optional[_Union[HealthCheck.TlsOptions, _Mapping]] = ...) -> None: ...
