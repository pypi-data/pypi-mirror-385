import datetime

from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.extensions.filters.network.http_connection_manager.v3 import http_connection_manager_pb2 as _http_connection_manager_pb2
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

class Router(_message.Message):
    __slots__ = ("dynamic_stats", "start_child_span", "upstream_log", "upstream_log_options", "suppress_envoy_headers", "strict_check_headers", "respect_expected_rq_timeout", "suppress_grpc_request_failure_code_stats", "upstream_http_filters")
    class UpstreamAccessLogOptions(_message.Message):
        __slots__ = ("flush_upstream_log_on_upstream_stream", "upstream_log_flush_interval")
        FLUSH_UPSTREAM_LOG_ON_UPSTREAM_STREAM_FIELD_NUMBER: _ClassVar[int]
        UPSTREAM_LOG_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        flush_upstream_log_on_upstream_stream: bool
        upstream_log_flush_interval: _duration_pb2.Duration
        def __init__(self, flush_upstream_log_on_upstream_stream: bool = ..., upstream_log_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    DYNAMIC_STATS_FIELD_NUMBER: _ClassVar[int]
    START_CHILD_SPAN_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_LOG_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_LOG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_ENVOY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    STRICT_CHECK_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESPECT_EXPECTED_RQ_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_GRPC_REQUEST_FAILURE_CODE_STATS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_HTTP_FILTERS_FIELD_NUMBER: _ClassVar[int]
    dynamic_stats: _wrappers_pb2.BoolValue
    start_child_span: bool
    upstream_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    upstream_log_options: Router.UpstreamAccessLogOptions
    suppress_envoy_headers: bool
    strict_check_headers: _containers.RepeatedScalarFieldContainer[str]
    respect_expected_rq_timeout: bool
    suppress_grpc_request_failure_code_stats: bool
    upstream_http_filters: _containers.RepeatedCompositeFieldContainer[_http_connection_manager_pb2.HttpFilter]
    def __init__(self, dynamic_stats: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., start_child_span: bool = ..., upstream_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., upstream_log_options: _Optional[_Union[Router.UpstreamAccessLogOptions, _Mapping]] = ..., suppress_envoy_headers: bool = ..., strict_check_headers: _Optional[_Iterable[str]] = ..., respect_expected_rq_timeout: bool = ..., suppress_grpc_request_failure_code_stats: bool = ..., upstream_http_filters: _Optional[_Iterable[_Union[_http_connection_manager_pb2.HttpFilter, _Mapping]]] = ...) -> None: ...
