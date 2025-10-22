import datetime

from envoy.config.common.matcher.v3 import matcher_pb2 as _matcher_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
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

class TapConfig(_message.Message):
    __slots__ = ("match_config", "match", "output_config", "tap_enabled")
    MATCH_CONFIG_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TAP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    match_config: MatchPredicate
    match: _matcher_pb2.MatchPredicate
    output_config: OutputConfig
    tap_enabled: _base_pb2.RuntimeFractionalPercent
    def __init__(self, match_config: _Optional[_Union[MatchPredicate, _Mapping]] = ..., match: _Optional[_Union[_matcher_pb2.MatchPredicate, _Mapping]] = ..., output_config: _Optional[_Union[OutputConfig, _Mapping]] = ..., tap_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ...) -> None: ...

class MatchPredicate(_message.Message):
    __slots__ = ("or_match", "and_match", "not_match", "any_match", "http_request_headers_match", "http_request_trailers_match", "http_response_headers_match", "http_response_trailers_match", "http_request_generic_body_match", "http_response_generic_body_match")
    class MatchSet(_message.Message):
        __slots__ = ("rules",)
        RULES_FIELD_NUMBER: _ClassVar[int]
        rules: _containers.RepeatedCompositeFieldContainer[MatchPredicate]
        def __init__(self, rules: _Optional[_Iterable[_Union[MatchPredicate, _Mapping]]] = ...) -> None: ...
    OR_MATCH_FIELD_NUMBER: _ClassVar[int]
    AND_MATCH_FIELD_NUMBER: _ClassVar[int]
    NOT_MATCH_FIELD_NUMBER: _ClassVar[int]
    ANY_MATCH_FIELD_NUMBER: _ClassVar[int]
    HTTP_REQUEST_HEADERS_MATCH_FIELD_NUMBER: _ClassVar[int]
    HTTP_REQUEST_TRAILERS_MATCH_FIELD_NUMBER: _ClassVar[int]
    HTTP_RESPONSE_HEADERS_MATCH_FIELD_NUMBER: _ClassVar[int]
    HTTP_RESPONSE_TRAILERS_MATCH_FIELD_NUMBER: _ClassVar[int]
    HTTP_REQUEST_GENERIC_BODY_MATCH_FIELD_NUMBER: _ClassVar[int]
    HTTP_RESPONSE_GENERIC_BODY_MATCH_FIELD_NUMBER: _ClassVar[int]
    or_match: MatchPredicate.MatchSet
    and_match: MatchPredicate.MatchSet
    not_match: MatchPredicate
    any_match: bool
    http_request_headers_match: HttpHeadersMatch
    http_request_trailers_match: HttpHeadersMatch
    http_response_headers_match: HttpHeadersMatch
    http_response_trailers_match: HttpHeadersMatch
    http_request_generic_body_match: HttpGenericBodyMatch
    http_response_generic_body_match: HttpGenericBodyMatch
    def __init__(self, or_match: _Optional[_Union[MatchPredicate.MatchSet, _Mapping]] = ..., and_match: _Optional[_Union[MatchPredicate.MatchSet, _Mapping]] = ..., not_match: _Optional[_Union[MatchPredicate, _Mapping]] = ..., any_match: bool = ..., http_request_headers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_request_trailers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_response_headers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_response_trailers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_request_generic_body_match: _Optional[_Union[HttpGenericBodyMatch, _Mapping]] = ..., http_response_generic_body_match: _Optional[_Union[HttpGenericBodyMatch, _Mapping]] = ...) -> None: ...

class HttpHeadersMatch(_message.Message):
    __slots__ = ("headers",)
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    headers: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    def __init__(self, headers: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ...) -> None: ...

class HttpGenericBodyMatch(_message.Message):
    __slots__ = ("bytes_limit", "patterns")
    class GenericTextMatch(_message.Message):
        __slots__ = ("string_match", "binary_match")
        STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
        BINARY_MATCH_FIELD_NUMBER: _ClassVar[int]
        string_match: str
        binary_match: bytes
        def __init__(self, string_match: _Optional[str] = ..., binary_match: _Optional[bytes] = ...) -> None: ...
    BYTES_LIMIT_FIELD_NUMBER: _ClassVar[int]
    PATTERNS_FIELD_NUMBER: _ClassVar[int]
    bytes_limit: int
    patterns: _containers.RepeatedCompositeFieldContainer[HttpGenericBodyMatch.GenericTextMatch]
    def __init__(self, bytes_limit: _Optional[int] = ..., patterns: _Optional[_Iterable[_Union[HttpGenericBodyMatch.GenericTextMatch, _Mapping]]] = ...) -> None: ...

class OutputConfig(_message.Message):
    __slots__ = ("sinks", "max_buffered_rx_bytes", "max_buffered_tx_bytes", "streaming", "min_streamed_sent_bytes")
    SINKS_FIELD_NUMBER: _ClassVar[int]
    MAX_BUFFERED_RX_BYTES_FIELD_NUMBER: _ClassVar[int]
    MAX_BUFFERED_TX_BYTES_FIELD_NUMBER: _ClassVar[int]
    STREAMING_FIELD_NUMBER: _ClassVar[int]
    MIN_STREAMED_SENT_BYTES_FIELD_NUMBER: _ClassVar[int]
    sinks: _containers.RepeatedCompositeFieldContainer[OutputSink]
    max_buffered_rx_bytes: _wrappers_pb2.UInt32Value
    max_buffered_tx_bytes: _wrappers_pb2.UInt32Value
    streaming: bool
    min_streamed_sent_bytes: _wrappers_pb2.UInt32Value
    def __init__(self, sinks: _Optional[_Iterable[_Union[OutputSink, _Mapping]]] = ..., max_buffered_rx_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_buffered_tx_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., streaming: bool = ..., min_streamed_sent_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class OutputSink(_message.Message):
    __slots__ = ("format", "streaming_admin", "file_per_tap", "streaming_grpc", "buffered_admin", "custom_sink")
    class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        JSON_BODY_AS_BYTES: _ClassVar[OutputSink.Format]
        JSON_BODY_AS_STRING: _ClassVar[OutputSink.Format]
        PROTO_BINARY: _ClassVar[OutputSink.Format]
        PROTO_BINARY_LENGTH_DELIMITED: _ClassVar[OutputSink.Format]
        PROTO_TEXT: _ClassVar[OutputSink.Format]
    JSON_BODY_AS_BYTES: OutputSink.Format
    JSON_BODY_AS_STRING: OutputSink.Format
    PROTO_BINARY: OutputSink.Format
    PROTO_BINARY_LENGTH_DELIMITED: OutputSink.Format
    PROTO_TEXT: OutputSink.Format
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    STREAMING_ADMIN_FIELD_NUMBER: _ClassVar[int]
    FILE_PER_TAP_FIELD_NUMBER: _ClassVar[int]
    STREAMING_GRPC_FIELD_NUMBER: _ClassVar[int]
    BUFFERED_ADMIN_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_SINK_FIELD_NUMBER: _ClassVar[int]
    format: OutputSink.Format
    streaming_admin: StreamingAdminSink
    file_per_tap: FilePerTapSink
    streaming_grpc: StreamingGrpcSink
    buffered_admin: BufferedAdminSink
    custom_sink: _extension_pb2.TypedExtensionConfig
    def __init__(self, format: _Optional[_Union[OutputSink.Format, str]] = ..., streaming_admin: _Optional[_Union[StreamingAdminSink, _Mapping]] = ..., file_per_tap: _Optional[_Union[FilePerTapSink, _Mapping]] = ..., streaming_grpc: _Optional[_Union[StreamingGrpcSink, _Mapping]] = ..., buffered_admin: _Optional[_Union[BufferedAdminSink, _Mapping]] = ..., custom_sink: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...

class StreamingAdminSink(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BufferedAdminSink(_message.Message):
    __slots__ = ("max_traces", "timeout")
    MAX_TRACES_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    max_traces: int
    timeout: _duration_pb2.Duration
    def __init__(self, max_traces: _Optional[int] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class FilePerTapSink(_message.Message):
    __slots__ = ("path_prefix",)
    PATH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    path_prefix: str
    def __init__(self, path_prefix: _Optional[str] = ...) -> None: ...

class StreamingGrpcSink(_message.Message):
    __slots__ = ("tap_id", "grpc_service")
    TAP_ID_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    tap_id: str
    grpc_service: _grpc_service_pb2.GrpcService
    def __init__(self, tap_id: _Optional[str] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ...) -> None: ...
