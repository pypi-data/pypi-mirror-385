from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import grpc_service_pb2 as _grpc_service_pb2
from envoy.api.v2.route import route_components_pb2 as _route_components_pb2
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

class TapConfig(_message.Message):
    __slots__ = ("match_config", "output_config", "tap_enabled")
    MATCH_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TAP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    match_config: MatchPredicate
    output_config: OutputConfig
    tap_enabled: _base_pb2.RuntimeFractionalPercent
    def __init__(self, match_config: _Optional[_Union[MatchPredicate, _Mapping]] = ..., output_config: _Optional[_Union[OutputConfig, _Mapping]] = ..., tap_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ...) -> None: ...

class MatchPredicate(_message.Message):
    __slots__ = ("or_match", "and_match", "not_match", "any_match", "http_request_headers_match", "http_request_trailers_match", "http_response_headers_match", "http_response_trailers_match")
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
    or_match: MatchPredicate.MatchSet
    and_match: MatchPredicate.MatchSet
    not_match: MatchPredicate
    any_match: bool
    http_request_headers_match: HttpHeadersMatch
    http_request_trailers_match: HttpHeadersMatch
    http_response_headers_match: HttpHeadersMatch
    http_response_trailers_match: HttpHeadersMatch
    def __init__(self, or_match: _Optional[_Union[MatchPredicate.MatchSet, _Mapping]] = ..., and_match: _Optional[_Union[MatchPredicate.MatchSet, _Mapping]] = ..., not_match: _Optional[_Union[MatchPredicate, _Mapping]] = ..., any_match: bool = ..., http_request_headers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_request_trailers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_response_headers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ..., http_response_trailers_match: _Optional[_Union[HttpHeadersMatch, _Mapping]] = ...) -> None: ...

class HttpHeadersMatch(_message.Message):
    __slots__ = ("headers",)
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    headers: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    def __init__(self, headers: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ...) -> None: ...

class OutputConfig(_message.Message):
    __slots__ = ("sinks", "max_buffered_rx_bytes", "max_buffered_tx_bytes", "streaming")
    SINKS_FIELD_NUMBER: _ClassVar[int]
    MAX_BUFFERED_RX_BYTES_FIELD_NUMBER: _ClassVar[int]
    MAX_BUFFERED_TX_BYTES_FIELD_NUMBER: _ClassVar[int]
    STREAMING_FIELD_NUMBER: _ClassVar[int]
    sinks: _containers.RepeatedCompositeFieldContainer[OutputSink]
    max_buffered_rx_bytes: _wrappers_pb2.UInt32Value
    max_buffered_tx_bytes: _wrappers_pb2.UInt32Value
    streaming: bool
    def __init__(self, sinks: _Optional[_Iterable[_Union[OutputSink, _Mapping]]] = ..., max_buffered_rx_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_buffered_tx_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., streaming: bool = ...) -> None: ...

class OutputSink(_message.Message):
    __slots__ = ("format", "streaming_admin", "file_per_tap", "streaming_grpc")
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
    format: OutputSink.Format
    streaming_admin: StreamingAdminSink
    file_per_tap: FilePerTapSink
    streaming_grpc: StreamingGrpcSink
    def __init__(self, format: _Optional[_Union[OutputSink.Format, str]] = ..., streaming_admin: _Optional[_Union[StreamingAdminSink, _Mapping]] = ..., file_per_tap: _Optional[_Union[FilePerTapSink, _Mapping]] = ..., streaming_grpc: _Optional[_Union[StreamingGrpcSink, _Mapping]] = ...) -> None: ...

class StreamingAdminSink(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

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
