from envoy.config.common.matcher.v3 import matcher_pb2 as _matcher_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import protocol_pb2 as _protocol_pb2
from envoy.extensions.filters.network.http_connection_manager.v3 import http_connection_manager_pb2 as _http_connection_manager_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpProtocolOptions(_message.Message):
    __slots__ = ("common_http_protocol_options", "upstream_http_protocol_options", "explicit_http_config", "use_downstream_protocol_config", "auto_config", "http_filters", "header_validation_config", "outlier_detection")
    class ExplicitHttpConfig(_message.Message):
        __slots__ = ("http_protocol_options", "http2_protocol_options", "http3_protocol_options")
        HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HTTP3_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        http_protocol_options: _protocol_pb2.Http1ProtocolOptions
        http2_protocol_options: _protocol_pb2.Http2ProtocolOptions
        http3_protocol_options: _protocol_pb2.Http3ProtocolOptions
        def __init__(self, http_protocol_options: _Optional[_Union[_protocol_pb2.Http1ProtocolOptions, _Mapping]] = ..., http2_protocol_options: _Optional[_Union[_protocol_pb2.Http2ProtocolOptions, _Mapping]] = ..., http3_protocol_options: _Optional[_Union[_protocol_pb2.Http3ProtocolOptions, _Mapping]] = ...) -> None: ...
    class UseDownstreamHttpConfig(_message.Message):
        __slots__ = ("http_protocol_options", "http2_protocol_options", "http3_protocol_options")
        HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HTTP3_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        http_protocol_options: _protocol_pb2.Http1ProtocolOptions
        http2_protocol_options: _protocol_pb2.Http2ProtocolOptions
        http3_protocol_options: _protocol_pb2.Http3ProtocolOptions
        def __init__(self, http_protocol_options: _Optional[_Union[_protocol_pb2.Http1ProtocolOptions, _Mapping]] = ..., http2_protocol_options: _Optional[_Union[_protocol_pb2.Http2ProtocolOptions, _Mapping]] = ..., http3_protocol_options: _Optional[_Union[_protocol_pb2.Http3ProtocolOptions, _Mapping]] = ...) -> None: ...
    class AutoHttpConfig(_message.Message):
        __slots__ = ("http_protocol_options", "http2_protocol_options", "http3_protocol_options", "alternate_protocols_cache_options")
        HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        HTTP3_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        ALTERNATE_PROTOCOLS_CACHE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        http_protocol_options: _protocol_pb2.Http1ProtocolOptions
        http2_protocol_options: _protocol_pb2.Http2ProtocolOptions
        http3_protocol_options: _protocol_pb2.Http3ProtocolOptions
        alternate_protocols_cache_options: _protocol_pb2.AlternateProtocolsCacheOptions
        def __init__(self, http_protocol_options: _Optional[_Union[_protocol_pb2.Http1ProtocolOptions, _Mapping]] = ..., http2_protocol_options: _Optional[_Union[_protocol_pb2.Http2ProtocolOptions, _Mapping]] = ..., http3_protocol_options: _Optional[_Union[_protocol_pb2.Http3ProtocolOptions, _Mapping]] = ..., alternate_protocols_cache_options: _Optional[_Union[_protocol_pb2.AlternateProtocolsCacheOptions, _Mapping]] = ...) -> None: ...
    class OutlierDetection(_message.Message):
        __slots__ = ("error_matcher",)
        ERROR_MATCHER_FIELD_NUMBER: _ClassVar[int]
        error_matcher: _matcher_pb2.MatchPredicate
        def __init__(self, error_matcher: _Optional[_Union[_matcher_pb2.MatchPredicate, _Mapping]] = ...) -> None: ...
    COMMON_HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    EXPLICIT_HTTP_CONFIG_FIELD_NUMBER: _ClassVar[int]
    USE_DOWNSTREAM_PROTOCOL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    AUTO_CONFIG_FIELD_NUMBER: _ClassVar[int]
    HTTP_FILTERS_FIELD_NUMBER: _ClassVar[int]
    HEADER_VALIDATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OUTLIER_DETECTION_FIELD_NUMBER: _ClassVar[int]
    common_http_protocol_options: _protocol_pb2.HttpProtocolOptions
    upstream_http_protocol_options: _protocol_pb2.UpstreamHttpProtocolOptions
    explicit_http_config: HttpProtocolOptions.ExplicitHttpConfig
    use_downstream_protocol_config: HttpProtocolOptions.UseDownstreamHttpConfig
    auto_config: HttpProtocolOptions.AutoHttpConfig
    http_filters: _containers.RepeatedCompositeFieldContainer[_http_connection_manager_pb2.HttpFilter]
    header_validation_config: _extension_pb2.TypedExtensionConfig
    outlier_detection: HttpProtocolOptions.OutlierDetection
    def __init__(self, common_http_protocol_options: _Optional[_Union[_protocol_pb2.HttpProtocolOptions, _Mapping]] = ..., upstream_http_protocol_options: _Optional[_Union[_protocol_pb2.UpstreamHttpProtocolOptions, _Mapping]] = ..., explicit_http_config: _Optional[_Union[HttpProtocolOptions.ExplicitHttpConfig, _Mapping]] = ..., use_downstream_protocol_config: _Optional[_Union[HttpProtocolOptions.UseDownstreamHttpConfig, _Mapping]] = ..., auto_config: _Optional[_Union[HttpProtocolOptions.AutoHttpConfig, _Mapping]] = ..., http_filters: _Optional[_Iterable[_Union[_http_connection_manager_pb2.HttpFilter, _Mapping]]] = ..., header_validation_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., outlier_detection: _Optional[_Union[HttpProtocolOptions.OutlierDetection, _Mapping]] = ...) -> None: ...
