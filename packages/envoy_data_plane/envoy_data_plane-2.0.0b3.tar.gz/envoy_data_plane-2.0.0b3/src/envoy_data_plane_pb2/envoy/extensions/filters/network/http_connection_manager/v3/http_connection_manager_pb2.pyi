import datetime

from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import protocol_pb2 as _protocol_pb2
from envoy.config.core.v3 import substitution_format_string_pb2 as _substitution_format_string_pb2
from envoy.config.route.v3 import route_pb2 as _route_pb2
from envoy.config.route.v3 import scoped_route_pb2 as _scoped_route_pb2
from envoy.config.trace.v3 import http_tracer_pb2 as _http_tracer_pb2
from envoy.type.http.v3 import path_transformation_pb2 as _path_transformation_pb2
from envoy.type.tracing.v3 import custom_tag_pb2 as _custom_tag_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import security_pb2 as _security_pb2
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

class HttpConnectionManager(_message.Message):
    __slots__ = ("codec_type", "stat_prefix", "rds", "route_config", "scoped_routes", "http_filters", "add_user_agent", "tracing", "common_http_protocol_options", "http1_safe_max_connection_duration", "http_protocol_options", "http2_protocol_options", "http3_protocol_options", "server_name", "server_header_transformation", "scheme_header_transformation", "max_request_headers_kb", "stream_idle_timeout", "stream_flush_timeout", "request_timeout", "request_headers_timeout", "drain_timeout", "delayed_close_timeout", "access_log", "access_log_flush_interval", "flush_access_log_on_new_request", "access_log_options", "use_remote_address", "xff_num_trusted_hops", "original_ip_detection_extensions", "early_header_mutation_extensions", "internal_address_config", "skip_xff_append", "via", "generate_request_id", "preserve_external_request_id", "always_set_request_id_in_response", "forward_client_cert_details", "set_current_client_cert_details", "proxy_100_continue", "represent_ipv4_remote_address_as_ipv4_mapped_ipv6", "upgrade_configs", "normalize_path", "merge_slashes", "path_with_escaped_slashes_action", "request_id_extension", "local_reply_config", "strip_matching_host_port", "strip_any_host_port", "stream_error_on_invalid_http_message", "path_normalization_options", "strip_trailing_host_dot", "proxy_status_config", "typed_header_validation_config", "append_x_forwarded_port", "append_local_overload", "add_proxy_protocol_connection_state")
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
    class PathWithEscapedSlashesAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IMPLEMENTATION_SPECIFIC_DEFAULT: _ClassVar[HttpConnectionManager.PathWithEscapedSlashesAction]
        KEEP_UNCHANGED: _ClassVar[HttpConnectionManager.PathWithEscapedSlashesAction]
        REJECT_REQUEST: _ClassVar[HttpConnectionManager.PathWithEscapedSlashesAction]
        UNESCAPE_AND_REDIRECT: _ClassVar[HttpConnectionManager.PathWithEscapedSlashesAction]
        UNESCAPE_AND_FORWARD: _ClassVar[HttpConnectionManager.PathWithEscapedSlashesAction]
    IMPLEMENTATION_SPECIFIC_DEFAULT: HttpConnectionManager.PathWithEscapedSlashesAction
    KEEP_UNCHANGED: HttpConnectionManager.PathWithEscapedSlashesAction
    REJECT_REQUEST: HttpConnectionManager.PathWithEscapedSlashesAction
    UNESCAPE_AND_REDIRECT: HttpConnectionManager.PathWithEscapedSlashesAction
    UNESCAPE_AND_FORWARD: HttpConnectionManager.PathWithEscapedSlashesAction
    class Tracing(_message.Message):
        __slots__ = ("client_sampling", "random_sampling", "overall_sampling", "verbose", "max_path_tag_length", "custom_tags", "provider", "spawn_upstream_span")
        class OperationName(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            INGRESS: _ClassVar[HttpConnectionManager.Tracing.OperationName]
            EGRESS: _ClassVar[HttpConnectionManager.Tracing.OperationName]
        INGRESS: HttpConnectionManager.Tracing.OperationName
        EGRESS: HttpConnectionManager.Tracing.OperationName
        CLIENT_SAMPLING_FIELD_NUMBER: _ClassVar[int]
        RANDOM_SAMPLING_FIELD_NUMBER: _ClassVar[int]
        OVERALL_SAMPLING_FIELD_NUMBER: _ClassVar[int]
        VERBOSE_FIELD_NUMBER: _ClassVar[int]
        MAX_PATH_TAG_LENGTH_FIELD_NUMBER: _ClassVar[int]
        CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
        PROVIDER_FIELD_NUMBER: _ClassVar[int]
        SPAWN_UPSTREAM_SPAN_FIELD_NUMBER: _ClassVar[int]
        client_sampling: _percent_pb2.Percent
        random_sampling: _percent_pb2.Percent
        overall_sampling: _percent_pb2.Percent
        verbose: bool
        max_path_tag_length: _wrappers_pb2.UInt32Value
        custom_tags: _containers.RepeatedCompositeFieldContainer[_custom_tag_pb2.CustomTag]
        provider: _http_tracer_pb2.Tracing.Http
        spawn_upstream_span: _wrappers_pb2.BoolValue
        def __init__(self, client_sampling: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., random_sampling: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., overall_sampling: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., verbose: bool = ..., max_path_tag_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., custom_tags: _Optional[_Iterable[_Union[_custom_tag_pb2.CustomTag, _Mapping]]] = ..., provider: _Optional[_Union[_http_tracer_pb2.Tracing.Http, _Mapping]] = ..., spawn_upstream_span: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    class InternalAddressConfig(_message.Message):
        __slots__ = ("unix_sockets", "cidr_ranges")
        UNIX_SOCKETS_FIELD_NUMBER: _ClassVar[int]
        CIDR_RANGES_FIELD_NUMBER: _ClassVar[int]
        unix_sockets: bool
        cidr_ranges: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
        def __init__(self, unix_sockets: bool = ..., cidr_ranges: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ...) -> None: ...
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
    class PathNormalizationOptions(_message.Message):
        __slots__ = ("forwarding_transformation", "http_filter_transformation")
        FORWARDING_TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
        HTTP_FILTER_TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
        forwarding_transformation: _path_transformation_pb2.PathTransformation
        http_filter_transformation: _path_transformation_pb2.PathTransformation
        def __init__(self, forwarding_transformation: _Optional[_Union[_path_transformation_pb2.PathTransformation, _Mapping]] = ..., http_filter_transformation: _Optional[_Union[_path_transformation_pb2.PathTransformation, _Mapping]] = ...) -> None: ...
    class ProxyStatusConfig(_message.Message):
        __slots__ = ("remove_details", "remove_connection_termination_details", "remove_response_flags", "set_recommended_response_code", "use_node_id", "literal_proxy_name")
        REMOVE_DETAILS_FIELD_NUMBER: _ClassVar[int]
        REMOVE_CONNECTION_TERMINATION_DETAILS_FIELD_NUMBER: _ClassVar[int]
        REMOVE_RESPONSE_FLAGS_FIELD_NUMBER: _ClassVar[int]
        SET_RECOMMENDED_RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
        USE_NODE_ID_FIELD_NUMBER: _ClassVar[int]
        LITERAL_PROXY_NAME_FIELD_NUMBER: _ClassVar[int]
        remove_details: bool
        remove_connection_termination_details: bool
        remove_response_flags: bool
        set_recommended_response_code: bool
        use_node_id: bool
        literal_proxy_name: str
        def __init__(self, remove_details: bool = ..., remove_connection_termination_details: bool = ..., remove_response_flags: bool = ..., set_recommended_response_code: bool = ..., use_node_id: bool = ..., literal_proxy_name: _Optional[str] = ...) -> None: ...
    class HcmAccessLogOptions(_message.Message):
        __slots__ = ("access_log_flush_interval", "flush_access_log_on_new_request", "flush_log_on_tunnel_successfully_established")
        ACCESS_LOG_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        FLUSH_ACCESS_LOG_ON_NEW_REQUEST_FIELD_NUMBER: _ClassVar[int]
        FLUSH_LOG_ON_TUNNEL_SUCCESSFULLY_ESTABLISHED_FIELD_NUMBER: _ClassVar[int]
        access_log_flush_interval: _duration_pb2.Duration
        flush_access_log_on_new_request: bool
        flush_log_on_tunnel_successfully_established: bool
        def __init__(self, access_log_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., flush_access_log_on_new_request: bool = ..., flush_log_on_tunnel_successfully_established: bool = ...) -> None: ...
    CODEC_TYPE_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    RDS_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCOPED_ROUTES_FIELD_NUMBER: _ClassVar[int]
    HTTP_FILTERS_FIELD_NUMBER: _ClassVar[int]
    ADD_USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    COMMON_HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP1_SAFE_MAX_CONNECTION_DURATION_FIELD_NUMBER: _ClassVar[int]
    HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP3_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVER_HEADER_TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
    SCHEME_HEADER_TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
    MAX_REQUEST_HEADERS_KB_FIELD_NUMBER: _ClassVar[int]
    STREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    STREAM_FLUSH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DRAIN_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DELAYED_CLOSE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    FLUSH_ACCESS_LOG_ON_NEW_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    USE_REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    XFF_NUM_TRUSTED_HOPS_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_IP_DETECTION_EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    EARLY_HEADER_MUTATION_EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ADDRESS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SKIP_XFF_APPEND_FIELD_NUMBER: _ClassVar[int]
    VIA_FIELD_NUMBER: _ClassVar[int]
    GENERATE_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_EXTERNAL_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ALWAYS_SET_REQUEST_ID_IN_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    FORWARD_CLIENT_CERT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    SET_CURRENT_CLIENT_CERT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    PROXY_100_CONTINUE_FIELD_NUMBER: _ClassVar[int]
    REPRESENT_IPV4_REMOTE_ADDRESS_AS_IPV4_MAPPED_IPV6_FIELD_NUMBER: _ClassVar[int]
    UPGRADE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    NORMALIZE_PATH_FIELD_NUMBER: _ClassVar[int]
    MERGE_SLASHES_FIELD_NUMBER: _ClassVar[int]
    PATH_WITH_ESCAPED_SLASHES_ACTION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    LOCAL_REPLY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STRIP_MATCHING_HOST_PORT_FIELD_NUMBER: _ClassVar[int]
    STRIP_ANY_HOST_PORT_FIELD_NUMBER: _ClassVar[int]
    STREAM_ERROR_ON_INVALID_HTTP_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PATH_NORMALIZATION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    STRIP_TRAILING_HOST_DOT_FIELD_NUMBER: _ClassVar[int]
    PROXY_STATUS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_HEADER_VALIDATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    APPEND_X_FORWARDED_PORT_FIELD_NUMBER: _ClassVar[int]
    APPEND_LOCAL_OVERLOAD_FIELD_NUMBER: _ClassVar[int]
    ADD_PROXY_PROTOCOL_CONNECTION_STATE_FIELD_NUMBER: _ClassVar[int]
    codec_type: HttpConnectionManager.CodecType
    stat_prefix: str
    rds: Rds
    route_config: _route_pb2.RouteConfiguration
    scoped_routes: ScopedRoutes
    http_filters: _containers.RepeatedCompositeFieldContainer[HttpFilter]
    add_user_agent: _wrappers_pb2.BoolValue
    tracing: HttpConnectionManager.Tracing
    common_http_protocol_options: _protocol_pb2.HttpProtocolOptions
    http1_safe_max_connection_duration: bool
    http_protocol_options: _protocol_pb2.Http1ProtocolOptions
    http2_protocol_options: _protocol_pb2.Http2ProtocolOptions
    http3_protocol_options: _protocol_pb2.Http3ProtocolOptions
    server_name: str
    server_header_transformation: HttpConnectionManager.ServerHeaderTransformation
    scheme_header_transformation: _protocol_pb2.SchemeHeaderTransformation
    max_request_headers_kb: _wrappers_pb2.UInt32Value
    stream_idle_timeout: _duration_pb2.Duration
    stream_flush_timeout: _duration_pb2.Duration
    request_timeout: _duration_pb2.Duration
    request_headers_timeout: _duration_pb2.Duration
    drain_timeout: _duration_pb2.Duration
    delayed_close_timeout: _duration_pb2.Duration
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    access_log_flush_interval: _duration_pb2.Duration
    flush_access_log_on_new_request: bool
    access_log_options: HttpConnectionManager.HcmAccessLogOptions
    use_remote_address: _wrappers_pb2.BoolValue
    xff_num_trusted_hops: int
    original_ip_detection_extensions: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    early_header_mutation_extensions: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    internal_address_config: HttpConnectionManager.InternalAddressConfig
    skip_xff_append: bool
    via: str
    generate_request_id: _wrappers_pb2.BoolValue
    preserve_external_request_id: bool
    always_set_request_id_in_response: bool
    forward_client_cert_details: HttpConnectionManager.ForwardClientCertDetails
    set_current_client_cert_details: HttpConnectionManager.SetCurrentClientCertDetails
    proxy_100_continue: bool
    represent_ipv4_remote_address_as_ipv4_mapped_ipv6: bool
    upgrade_configs: _containers.RepeatedCompositeFieldContainer[HttpConnectionManager.UpgradeConfig]
    normalize_path: _wrappers_pb2.BoolValue
    merge_slashes: bool
    path_with_escaped_slashes_action: HttpConnectionManager.PathWithEscapedSlashesAction
    request_id_extension: RequestIDExtension
    local_reply_config: LocalReplyConfig
    strip_matching_host_port: bool
    strip_any_host_port: bool
    stream_error_on_invalid_http_message: _wrappers_pb2.BoolValue
    path_normalization_options: HttpConnectionManager.PathNormalizationOptions
    strip_trailing_host_dot: bool
    proxy_status_config: HttpConnectionManager.ProxyStatusConfig
    typed_header_validation_config: _extension_pb2.TypedExtensionConfig
    append_x_forwarded_port: bool
    append_local_overload: bool
    add_proxy_protocol_connection_state: _wrappers_pb2.BoolValue
    def __init__(self, codec_type: _Optional[_Union[HttpConnectionManager.CodecType, str]] = ..., stat_prefix: _Optional[str] = ..., rds: _Optional[_Union[Rds, _Mapping]] = ..., route_config: _Optional[_Union[_route_pb2.RouteConfiguration, _Mapping]] = ..., scoped_routes: _Optional[_Union[ScopedRoutes, _Mapping]] = ..., http_filters: _Optional[_Iterable[_Union[HttpFilter, _Mapping]]] = ..., add_user_agent: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., tracing: _Optional[_Union[HttpConnectionManager.Tracing, _Mapping]] = ..., common_http_protocol_options: _Optional[_Union[_protocol_pb2.HttpProtocolOptions, _Mapping]] = ..., http1_safe_max_connection_duration: bool = ..., http_protocol_options: _Optional[_Union[_protocol_pb2.Http1ProtocolOptions, _Mapping]] = ..., http2_protocol_options: _Optional[_Union[_protocol_pb2.Http2ProtocolOptions, _Mapping]] = ..., http3_protocol_options: _Optional[_Union[_protocol_pb2.Http3ProtocolOptions, _Mapping]] = ..., server_name: _Optional[str] = ..., server_header_transformation: _Optional[_Union[HttpConnectionManager.ServerHeaderTransformation, str]] = ..., scheme_header_transformation: _Optional[_Union[_protocol_pb2.SchemeHeaderTransformation, _Mapping]] = ..., max_request_headers_kb: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., stream_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., stream_flush_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., request_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., request_headers_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., drain_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., delayed_close_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., access_log_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., flush_access_log_on_new_request: bool = ..., access_log_options: _Optional[_Union[HttpConnectionManager.HcmAccessLogOptions, _Mapping]] = ..., use_remote_address: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., xff_num_trusted_hops: _Optional[int] = ..., original_ip_detection_extensions: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., early_header_mutation_extensions: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., internal_address_config: _Optional[_Union[HttpConnectionManager.InternalAddressConfig, _Mapping]] = ..., skip_xff_append: bool = ..., via: _Optional[str] = ..., generate_request_id: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., preserve_external_request_id: bool = ..., always_set_request_id_in_response: bool = ..., forward_client_cert_details: _Optional[_Union[HttpConnectionManager.ForwardClientCertDetails, str]] = ..., set_current_client_cert_details: _Optional[_Union[HttpConnectionManager.SetCurrentClientCertDetails, _Mapping]] = ..., proxy_100_continue: bool = ..., represent_ipv4_remote_address_as_ipv4_mapped_ipv6: bool = ..., upgrade_configs: _Optional[_Iterable[_Union[HttpConnectionManager.UpgradeConfig, _Mapping]]] = ..., normalize_path: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., merge_slashes: bool = ..., path_with_escaped_slashes_action: _Optional[_Union[HttpConnectionManager.PathWithEscapedSlashesAction, str]] = ..., request_id_extension: _Optional[_Union[RequestIDExtension, _Mapping]] = ..., local_reply_config: _Optional[_Union[LocalReplyConfig, _Mapping]] = ..., strip_matching_host_port: bool = ..., strip_any_host_port: bool = ..., stream_error_on_invalid_http_message: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., path_normalization_options: _Optional[_Union[HttpConnectionManager.PathNormalizationOptions, _Mapping]] = ..., strip_trailing_host_dot: bool = ..., proxy_status_config: _Optional[_Union[HttpConnectionManager.ProxyStatusConfig, _Mapping]] = ..., typed_header_validation_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., append_x_forwarded_port: bool = ..., append_local_overload: bool = ..., add_proxy_protocol_connection_state: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class LocalReplyConfig(_message.Message):
    __slots__ = ("mappers", "body_format")
    MAPPERS_FIELD_NUMBER: _ClassVar[int]
    BODY_FORMAT_FIELD_NUMBER: _ClassVar[int]
    mappers: _containers.RepeatedCompositeFieldContainer[ResponseMapper]
    body_format: _substitution_format_string_pb2.SubstitutionFormatString
    def __init__(self, mappers: _Optional[_Iterable[_Union[ResponseMapper, _Mapping]]] = ..., body_format: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ...) -> None: ...

class ResponseMapper(_message.Message):
    __slots__ = ("filter", "status_code", "body", "body_format_override", "headers_to_add")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    BODY_FORMAT_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    filter: _accesslog_pb2.AccessLogFilter
    status_code: _wrappers_pb2.UInt32Value
    body: _base_pb2.DataSource
    body_format_override: _substitution_format_string_pb2.SubstitutionFormatString
    headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    def __init__(self, filter: _Optional[_Union[_accesslog_pb2.AccessLogFilter, _Mapping]] = ..., status_code: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., body: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., body_format_override: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ..., headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("scoped_rds_config_source", "srds_resources_locator")
    SCOPED_RDS_CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SRDS_RESOURCES_LOCATOR_FIELD_NUMBER: _ClassVar[int]
    scoped_rds_config_source: _config_source_pb2.ConfigSource
    srds_resources_locator: str
    def __init__(self, scoped_rds_config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., srds_resources_locator: _Optional[str] = ...) -> None: ...

class HttpFilter(_message.Message):
    __slots__ = ("name", "typed_config", "config_discovery", "is_optional", "disabled")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DISCOVERY_FIELD_NUMBER: _ClassVar[int]
    IS_OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    config_discovery: _config_source_pb2.ExtensionConfigSource
    is_optional: bool
    disabled: bool
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., config_discovery: _Optional[_Union[_config_source_pb2.ExtensionConfigSource, _Mapping]] = ..., is_optional: bool = ..., disabled: bool = ...) -> None: ...

class RequestIDExtension(_message.Message):
    __slots__ = ("typed_config",)
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    typed_config: _any_pb2.Any
    def __init__(self, typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class EnvoyMobileHttpConnectionManager(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: HttpConnectionManager
    def __init__(self, config: _Optional[_Union[HttpConnectionManager, _Mapping]] = ...) -> None: ...
