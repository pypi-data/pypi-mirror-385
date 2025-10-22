from envoy.config.filter.accesslog.v2 import accesslog_pb2 as _accesslog_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Router(_message.Message):
    __slots__ = ("dynamic_stats", "start_child_span", "upstream_log", "suppress_envoy_headers", "strict_check_headers", "respect_expected_rq_timeout")
    DYNAMIC_STATS_FIELD_NUMBER: _ClassVar[int]
    START_CHILD_SPAN_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_LOG_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_ENVOY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    STRICT_CHECK_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESPECT_EXPECTED_RQ_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    dynamic_stats: _wrappers_pb2.BoolValue
    start_child_span: bool
    upstream_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    suppress_envoy_headers: bool
    strict_check_headers: _containers.RepeatedScalarFieldContainer[str]
    respect_expected_rq_timeout: bool
    def __init__(self, dynamic_stats: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., start_child_span: bool = ..., upstream_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., suppress_envoy_headers: bool = ..., strict_check_headers: _Optional[_Iterable[str]] = ..., respect_expected_rq_timeout: bool = ...) -> None: ...
