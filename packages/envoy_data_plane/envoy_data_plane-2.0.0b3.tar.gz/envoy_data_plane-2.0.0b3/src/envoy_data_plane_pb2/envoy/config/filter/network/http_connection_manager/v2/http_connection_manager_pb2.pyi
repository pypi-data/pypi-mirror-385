import datetime

from envoy.api.v2.core import config_source_pb2 as _config_source_pb2
from envoy.api.v2.core import protocol_pb2 as _protocol_pb2
from envoy.api.v2 import route_pb2 as _route_pb2
from envoy.api.v2 import scoped_route_pb2 as _scoped_route_pb2
from envoy.config.filter.accesslog.v2 import accesslog_pb2 as _accesslog_pb2
from envoy.config.trace.v2 import http_tracer_pb2 as _http_tracer_pb2
from envoy.type import percent_pb2 as _percent_pb2
from envoy.type.tracing.v2 import custom_tag_pb2 as _custom_tag_pb2
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

class HttpConnectionManager(_message.Message):
    __slots__ = ("codec_type", "stat_prefix", "rds", "route_config", "scoped_routes", "http_filters", "add_user_agent", "tracing", "common_http_protocol_options", "http_protocol_options", "http2_protocol_options", "server_name", "server_header_transformation", "max_request_headers_kb", "idle_timeout", "stream_idle_timeout", "request_timeout", "drain_timeout", "delayed_close_timeout", "access_log", "use_remote_address", "xff_num_trusted_hops", "internal_address_config", "skip_xff_append", "via", "generate_request_id", "preserve_external_request_id", "forward_client_cert_details", "set_current_client_cert_details", "proxy_100_continue", "represent_ipv4_remote_address_as_ipv4_mapped_ipv6", "upgrade_configs", "normalize_path", "merge_slashes", "request_id_extension")
    class CodecType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AUTO: _ClassVar[HttpConnectionManager.CodecType]
        HTTP1: _ClassVar[HttpConnectionManager.CodecType]
        HTTP2: _ClassVar[HttpConnectionManager.CodecType]
        HTTP3: _ClassVar[HttpConnectionManager.CodecType]
    AUTO: HttpConnectionManager.CodecType
    HTTP1: HttpConnectionManager.CodecType
    HTTP2: HttpConnectionManager.CodecType
    HTTP3: HttpConnectionManager.CodecType
    class ServerHeaderTransformation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OVERWRITE: _ClassVar[HttpConnectionManager.ServerHeaderTransformation]
        APPEND_IF_ABSENT: _ClassVar[HttpConnectionManager.ServerHeaderTransformation]
        PASS_THROUGH: _ClassVar[HttpConnectionManager.ServerHeaderTransformation]
    OVERWRITE: HttpConnectionManager.ServerHeaderTransformation
    APPEND_IF_ABSENT: HttpConnectionManager.ServerHeaderTransformation
    PASS_THROUGH: HttpConnectionManager.ServerHeaderTransformation
    class ForwardClientCertDetails(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SANITIZE: _ClassVar[HttpConnectionManager.ForwardClientCertDetails]
        FORWARD_ONLY: _ClassVar[HttpConnectionManager.ForwardClientCertDetails]
        APPEND_FORWARD: _ClassVar[HttpConnectionManager.ForwardClientCertDetails]
        SANITIZE_SET: _ClassVar[HttpConnectionManager.ForwardClientCertDetails]
        ALWAYS_FORWARD_ONLY: _ClassVar[HttpConnectionManager.ForwardClientCertDetails]
    SANITIZE: HttpConnectionManager.ForwardClientCertDetails
    FORWARD_ONLY: HttpConnectionManager.ForwardClientCertDetails
    APPEND_FORWARD: HttpConnectionManager.ForwardClientCertDetails
    SANITIZE_SET: HttpConnectionManager.ForwardClientCertDetails
    ALWAYS_FORWARD_ONLY: HttpConnectionManager.ForwardClientCertDetails
    class Tracing(_message.Message):
        __slots__ = ("operation_name", "request_headers_for_tags", "client_sampling", "random_sampling", "overall_sampling", "verbose", "max_path_tag_length", "custom_tags", "provider")
        class OperationName(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            INGRESS: _ClassVar[HttpConnectionManager.Tracing.OperationName]
            EGRESS: _ClassVar[HttpConnectionManager.Tracing.OperationName]
        INGRESS: HttpConnectionManager.Tracing.OperationName
        EGRESS: HttpConnectionManager.Tracing.OperationName
        OPERATION_NAME_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_FOR_TAGS_FIELD_NUMBER: _ClassVar[int]
        CLIENT_SAMPLING_FIELD_NUMBER: _ClassVar[int]
        RANDOM_SAMPLING_FIELD_NUMBER: _ClassVar[int]
        OVERALL_SAMPLING_FIELD_NUMBER: _ClassVar[int]
        VERBOSE_FIELD_NUMBER: _ClassVar[int]
        MAX_PATH_TAG_LENGTH_FIELD_NUMBER: _ClassVar[int]
        CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
        PROVIDER_FIELD_NUMBER: _ClassVar[int]
        operation_name: HttpConnectionManager.Tracing.OperationName
        request_headers_for_tags: _containers.RepeatedScalarFieldContainer[str]
        client_sampling: _percent_pb2.Percent
        random_sampling: _percent_pb2.Percent
        overall_sampling: _percent_pb2.Percent
        verbose: bool
        max_path_tag_length: _wrappers_pb2.UInt32Value
        custom_tags: _containers.RepeatedCompositeFieldContainer[_custom_tag_pb2.CustomTag]
        provider: _http_tracer_pb2.Tracing.Http
        def __init__(self, operation_name: _Optional[_Union[HttpConnectionManager.Tracing.OperationName, str]] = ..., request_headers_for_tags: _Optional[_Iterable[str]] = ..., client_sampling: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., random_sampling: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., overall_sampling: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., verbose: bool = ..., max_path_tag_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., custom_tags: _Optional[_Iterable[_Union[_custom_tag_pb2.CustomTag, _Mapping]]] = ..., provider: _Optional[_Union[_http_tracer_pb2.Tracing.Http, _Mapping]] = ...) -> None: ...
    class InternalAddressConfig(_message.Message):
        __slots__ = ("unix_sockets",)
        UNIX_SOCKETS_FIELD_NUMBER: _ClassVar[int]
        unix_sockets: bool
        def __init__(self, unix_sockets: bool = ...) -> None: ...
    class SetCurrentClientCertDetails(_message.Message):
        __slots__ = ("subject", "cert", "chain", "dns", "uri")
        SUBJECT_FIELD_NUMBER: _ClassVar[int]
        CERT_FIELD_NUMBER: _ClassVar[int]
        CHAIN_FIELD_NUMBER: _ClassVar[int]
        DNS_FIELD_NUMBER: _ClassVar[int]
        URI_FIELD_NUMBER: _ClassVar[int]
        subject: _wrappers_pb2.BoolValue
        cert: bool
        chain: bool
        dns: bool
        uri: bool
        def __init__(self, subject: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., cert: bool = ..., chain: bool = ..., dns: bool = ..., uri: bool = ...) -> None: ...
    class UpgradeConfig(_message.Message):
        __slots__ = ("upgrade_type", "filters", "enabled")
        UPGRADE_TYPE_FIELD_NUMBER: _ClassVar[int]
        FILTERS_FIELD_NUMBER: _ClassVar[int]
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        upgrade_type: str
        filters: _containers.RepeatedCompositeFieldContainer[HttpFilter]
        enabled: _wrappers_pb2.BoolValue
        def __init__(self, upgrade_type: _Optional[str] = ..., filters: _Optional[_Iterable[_Union[HttpFilter, _Mapping]]] = ..., enabled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    CODEC_TYPE_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    RDS_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCOPED_ROUTES_FIELD_NUMBER: _ClassVar[int]
    HTTP_FILTERS_FIELD_NUMBER: _ClassVar[int]
    ADD_USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    COMMON_HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVER_HEADER_TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
    MAX_REQUEST_HEADERS_KB_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    STREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DRAIN_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DELAYED_CLOSE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    USE_REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    XFF_NUM_TRUSTED_HOPS_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ADDRESS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SKIP_XFF_APPEND_FIELD_NUMBER: _ClassVar[int]
    VIA_FIELD_NUMBER: _ClassVar[int]
    GENERATE_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_EXTERNAL_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    FORWARD_CLIENT_CERT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    SET_CURRENT_CLIENT_CERT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    PROXY_100_CONTINUE_FIELD_NUMBER: _ClassVar[int]
    REPRESENT_IPV4_REMOTE_ADDRESS_AS_IPV4_MAPPED_IPV6_FIELD_NUMBER: _ClassVar[int]
    UPGRADE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    NORMALIZE_PATH_FIELD_NUMBER: _ClassVar[int]
    MERGE_SLASHES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    codec_type: HttpConnectionManager.CodecType
    stat_prefix: str
    rds: Rds
    route_config: _route_pb2.RouteConfiguration
    scoped_routes: ScopedRoutes
    http_filters: _containers.RepeatedCompositeFieldContainer[HttpFilter]
    add_user_agent: _wrappers_pb2.BoolValue
    tracing: HttpConnectionManager.Tracing
    common_http_protocol_options: _protocol_pb2.HttpProtocolOptions
    http_protocol_options: _protocol_pb2.Http1ProtocolOptions
    http2_protocol_options: _protocol_pb2.Http2ProtocolOptions
    server_name: str
    server_header_transformation: HttpConnectionManager.ServerHeaderTransformation
    max_request_headers_kb: _wrappers_pb2.UInt32Value
    idle_timeout: _duration_pb2.Duration
    stream_idle_timeout: _duration_pb2.Duration
    request_timeout: _duration_pb2.Duration
    drain_timeout: _duration_pb2.Duration
    delayed_close_timeout: _duration_pb2.Duration
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    use_remote_address: _wrappers_pb2.BoolValue
    xff_num_trusted_hops: int
    internal_address_config: HttpConnectionManager.InternalAddressConfig
    skip_xff_append: bool
    via: str
    generate_request_id: _wrappers_pb2.BoolValue
    preserve_external_request_id: bool
    forward_client_cert_details: HttpConnectionManager.ForwardClientCertDetails
    set_current_client_cert_details: HttpConnectionManager.SetCurrentClientCertDetails
    proxy_100_continue: bool
    represent_ipv4_remote_address_as_ipv4_mapped_ipv6: bool
    upgrade_configs: _containers.RepeatedCompositeFieldContainer[HttpConnectionManager.UpgradeConfig]
    normalize_path: _wrappers_pb2.BoolValue
    merge_slashes: bool
    request_id_extension: RequestIDExtension
    def __init__(self, codec_type: _Optional[_Union[HttpConnectionManager.CodecType, str]] = ..., stat_prefix: _Optional[str] = ..., rds: _Optional[_Union[Rds, _Mapping]] = ..., route_config: _Optional[_Union[_route_pb2.RouteConfiguration, _Mapping]] = ..., scoped_routes: _Optional[_Union[ScopedRoutes, _Mapping]] = ..., http_filters: _Optional[_Iterable[_Union[HttpFilter, _Mapping]]] = ..., add_user_agent: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., tracing: _Optional[_Union[HttpConnectionManager.Tracing, _Mapping]] = ..., common_http_protocol_options: _Optional[_Union[_protocol_pb2.HttpProtocolOptions, _Mapping]] = ..., http_protocol_options: _Optional[_Union[_protocol_pb2.Http1ProtocolOptions, _Mapping]] = ..., http2_protocol_options: _Optional[_Union[_protocol_pb2.Http2ProtocolOptions, _Mapping]] = ..., server_name: _Optional[str] = ..., server_header_transformation: _Optional[_Union[HttpConnectionManager.ServerHeaderTransformation, str]] = ..., max_request_headers_kb: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., stream_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., request_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., drain_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., delayed_close_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., use_remote_address: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., xff_num_trusted_hops: _Optional[int] = ..., internal_address_config: _Optional[_Union[HttpConnectionManager.InternalAddressConfig, _Mapping]] = ..., skip_xff_append: bool = ..., via: _Optional[str] = ..., generate_request_id: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., preserve_external_request_id: bool = ..., forward_client_cert_details: _Optional[_Union[HttpConnectionManager.ForwardClientCertDetails, str]] = ..., set_current_client_cert_details: _Optional[_Union[HttpConnectionManager.SetCurrentClientCertDetails, _Mapping]] = ..., proxy_100_continue: bool = ..., represent_ipv4_remote_address_as_ipv4_mapped_ipv6: bool = ..., upgrade_configs: _Optional[_Iterable[_Union[HttpConnectionManager.UpgradeConfig, _Mapping]]] = ..., normalize_path: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., merge_slashes: bool = ..., request_id_extension: _Optional[_Union[RequestIDExtension, _Mapping]] = ...) -> None: ...

class Rds(_message.Message):
    __slots__ = ("config_source", "route_config_name")
    CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_NAME_FIELD_NUMBER: _ClassVar[int]
    config_source: _config_source_pb2.ConfigSource
    route_config_name: str
    def __init__(self, config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., route_config_name: _Optional[str] = ...) -> None: ...

class ScopedRouteConfigurationsList(_message.Message):
    __slots__ = ("scoped_route_configurations",)
    SCOPED_ROUTE_CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    scoped_route_configurations: _containers.RepeatedCompositeFieldContainer[_scoped_route_pb2.ScopedRouteConfiguration]
    def __init__(self, scoped_route_configurations: _Optional[_Iterable[_Union[_scoped_route_pb2.ScopedRouteConfiguration, _Mapping]]] = ...) -> None: ...

class ScopedRoutes(_message.Message):
    __slots__ = ("name", "scope_key_builder", "rds_config_source", "scoped_route_configurations_list", "scoped_rds")
    class ScopeKeyBuilder(_message.Message):
        __slots__ = ("fragments",)
        class FragmentBuilder(_message.Message):
            __slots__ = ("header_value_extractor",)
            class HeaderValueExtractor(_message.Message):
                __slots__ = ("name", "element_separator", "index", "element")
                class KvElement(_message.Message):
                    __slots__ = ("separator", "key")
                    SEPARATOR_FIELD_NUMBER: _ClassVar[int]
                    KEY_FIELD_NUMBER: _ClassVar[int]
                    separator: str
                    key: str
                    def __init__(self, separator: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...
                NAME_FIELD_NUMBER: _ClassVar[int]
                ELEMENT_SEPARATOR_FIELD_NUMBER: _ClassVar[int]
                INDEX_FIELD_NUMBER: _ClassVar[int]
                ELEMENT_FIELD_NUMBER: _ClassVar[int]
                name: str
                element_separator: str
                index: int
                element: ScopedRoutes.ScopeKeyBuilder.FragmentBuilder.HeaderValueExtractor.KvElement
                def __init__(self, name: _Optional[str] = ..., element_separator: _Optional[str] = ..., index: _Optional[int] = ..., element: _Optional[_Union[ScopedRoutes.ScopeKeyBuilder.FragmentBuilder.HeaderValueExtractor.KvElement, _Mapping]] = ...) -> None: ...
            HEADER_VALUE_EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
            header_value_extractor: ScopedRoutes.ScopeKeyBuilder.FragmentBuilder.HeaderValueExtractor
            def __init__(self, header_value_extractor: _Optional[_Union[ScopedRoutes.ScopeKeyBuilder.FragmentBuilder.HeaderValueExtractor, _Mapping]] = ...) -> None: ...
        FRAGMENTS_FIELD_NUMBER: _ClassVar[int]
        fragments: _containers.RepeatedCompositeFieldContainer[ScopedRoutes.ScopeKeyBuilder.FragmentBuilder]
        def __init__(self, fragments: _Optional[_Iterable[_Union[ScopedRoutes.ScopeKeyBuilder.FragmentBuilder, _Mapping]]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCOPE_KEY_BUILDER_FIELD_NUMBER: _ClassVar[int]
    RDS_CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SCOPED_ROUTE_CONFIGURATIONS_LIST_FIELD_NUMBER: _ClassVar[int]
    SCOPED_RDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    scope_key_builder: ScopedRoutes.ScopeKeyBuilder
    rds_config_source: _config_source_pb2.ConfigSource
    scoped_route_configurations_list: ScopedRouteConfigurationsList
    scoped_rds: ScopedRds
    def __init__(self, name: _Optional[str] = ..., scope_key_builder: _Optional[_Union[ScopedRoutes.ScopeKeyBuilder, _Mapping]] = ..., rds_config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., scoped_route_configurations_list: _Optional[_Union[ScopedRouteConfigurationsList, _Mapping]] = ..., scoped_rds: _Optional[_Union[ScopedRds, _Mapping]] = ...) -> None: ...

class ScopedRds(_message.Message):
    __slots__ = ("scoped_rds_config_source",)
    SCOPED_RDS_CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    scoped_rds_config_source: _config_source_pb2.ConfigSource
    def __init__(self, scoped_rds_config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ...) -> None: ...

class HttpFilter(_message.Message):
    __slots__ = ("name", "config", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _struct_pb2.Struct
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class RequestIDExtension(_message.Message):
    __slots__ = ("typed_config",)
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    typed_config: _any_pb2.Any
    def __init__(self, typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
