from envoy.config.common.mutation_rules.v3 import mutation_rules_pb2 as _mutation_rules_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.config.core.v3 import http_uri_pb2 as _http_uri_pb2
from envoy.type.matcher.v3 import metadata_pb2 as _metadata_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtAuthz(_message.Message):
    __slots__ = ("grpc_service", "http_service", "transport_api_version", "failure_mode_allow", "failure_mode_allow_header_add", "with_request_body", "clear_route_cache", "status_on_error", "validate_mutations", "metadata_context_namespaces", "typed_metadata_context_namespaces", "route_metadata_context_namespaces", "route_typed_metadata_context_namespaces", "filter_enabled", "filter_enabled_metadata", "deny_at_disable", "include_peer_certificate", "stat_prefix", "bootstrap_metadata_labels_key", "allowed_headers", "disallowed_headers", "include_tls_session", "charge_cluster_response_stats", "encode_raw_headers", "decoder_header_mutation_rules", "enable_dynamic_metadata_ingestion", "filter_metadata", "emit_filter_state_stats", "max_denied_response_body_bytes")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_HEADER_ADD_FIELD_NUMBER: _ClassVar[int]
    WITH_REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    CLEAR_ROUTE_CACHE_FIELD_NUMBER: _ClassVar[int]
    STATUS_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    METADATA_CONTEXT_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    TYPED_METADATA_CONTEXT_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    ROUTE_METADATA_CONTEXT_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    ROUTE_TYPED_METADATA_CONTEXT_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_METADATA_FIELD_NUMBER: _ClassVar[int]
    DENY_AT_DISABLE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PEER_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_METADATA_LABELS_KEY_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    DISALLOWED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_TLS_SESSION_FIELD_NUMBER: _ClassVar[int]
    CHARGE_CLUSTER_RESPONSE_STATS_FIELD_NUMBER: _ClassVar[int]
    ENCODE_RAW_HEADERS_FIELD_NUMBER: _ClassVar[int]
    DECODER_HEADER_MUTATION_RULES_FIELD_NUMBER: _ClassVar[int]
    ENABLE_DYNAMIC_METADATA_INGESTION_FIELD_NUMBER: _ClassVar[int]
    FILTER_METADATA_FIELD_NUMBER: _ClassVar[int]
    EMIT_FILTER_STATE_STATS_FIELD_NUMBER: _ClassVar[int]
    MAX_DENIED_RESPONSE_BODY_BYTES_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    http_service: HttpService
    transport_api_version: _config_source_pb2.ApiVersion
    failure_mode_allow: bool
    failure_mode_allow_header_add: bool
    with_request_body: BufferSettings
    clear_route_cache: bool
    status_on_error: _http_status_pb2.HttpStatus
    validate_mutations: bool
    metadata_context_namespaces: _containers.RepeatedScalarFieldContainer[str]
    typed_metadata_context_namespaces: _containers.RepeatedScalarFieldContainer[str]
    route_metadata_context_namespaces: _containers.RepeatedScalarFieldContainer[str]
    route_typed_metadata_context_namespaces: _containers.RepeatedScalarFieldContainer[str]
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    filter_enabled_metadata: _metadata_pb2.MetadataMatcher
    deny_at_disable: _base_pb2.RuntimeFeatureFlag
    include_peer_certificate: bool
    stat_prefix: str
    bootstrap_metadata_labels_key: str
    allowed_headers: _string_pb2.ListStringMatcher
    disallowed_headers: _string_pb2.ListStringMatcher
    include_tls_session: bool
    charge_cluster_response_stats: _wrappers_pb2.BoolValue
    encode_raw_headers: bool
    decoder_header_mutation_rules: _mutation_rules_pb2.HeaderMutationRules
    enable_dynamic_metadata_ingestion: _wrappers_pb2.BoolValue
    filter_metadata: _struct_pb2.Struct
    emit_filter_state_stats: bool
    max_denied_response_body_bytes: int
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., http_service: _Optional[_Union[HttpService, _Mapping]] = ..., transport_api_version: _Optional[_Union[_config_source_pb2.ApiVersion, str]] = ..., failure_mode_allow: bool = ..., failure_mode_allow_header_add: bool = ..., with_request_body: _Optional[_Union[BufferSettings, _Mapping]] = ..., clear_route_cache: bool = ..., status_on_error: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., validate_mutations: bool = ..., metadata_context_namespaces: _Optional[_Iterable[str]] = ..., typed_metadata_context_namespaces: _Optional[_Iterable[str]] = ..., route_metadata_context_namespaces: _Optional[_Iterable[str]] = ..., route_typed_metadata_context_namespaces: _Optional[_Iterable[str]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., filter_enabled_metadata: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., deny_at_disable: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., include_peer_certificate: bool = ..., stat_prefix: _Optional[str] = ..., bootstrap_metadata_labels_key: _Optional[str] = ..., allowed_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., disallowed_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., include_tls_session: bool = ..., charge_cluster_response_stats: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., encode_raw_headers: bool = ..., decoder_header_mutation_rules: _Optional[_Union[_mutation_rules_pb2.HeaderMutationRules, _Mapping]] = ..., enable_dynamic_metadata_ingestion: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., filter_metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., emit_filter_state_stats: bool = ..., max_denied_response_body_bytes: _Optional[int] = ...) -> None: ...

class BufferSettings(_message.Message):
    __slots__ = ("max_request_bytes", "allow_partial_message", "pack_as_bytes")
    MAX_REQUEST_BYTES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PACK_AS_BYTES_FIELD_NUMBER: _ClassVar[int]
    max_request_bytes: int
    allow_partial_message: bool
    pack_as_bytes: bool
    def __init__(self, max_request_bytes: _Optional[int] = ..., allow_partial_message: bool = ..., pack_as_bytes: bool = ...) -> None: ...

class HttpService(_message.Message):
    __slots__ = ("server_uri", "path_prefix", "authorization_request", "authorization_response", "retry_policy")
    SERVER_URI_FIELD_NUMBER: _ClassVar[int]
    PATH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    server_uri: _http_uri_pb2.HttpUri
    path_prefix: str
    authorization_request: AuthorizationRequest
    authorization_response: AuthorizationResponse
    retry_policy: _base_pb2.RetryPolicy
    def __init__(self, server_uri: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., path_prefix: _Optional[str] = ..., authorization_request: _Optional[_Union[AuthorizationRequest, _Mapping]] = ..., authorization_response: _Optional[_Union[AuthorizationResponse, _Mapping]] = ..., retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ...) -> None: ...

class AuthorizationRequest(_message.Message):
    __slots__ = ("allowed_headers", "headers_to_add")
    ALLOWED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    allowed_headers: _string_pb2.ListStringMatcher
    headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
    def __init__(self, allowed_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ...) -> None: ...

class AuthorizationResponse(_message.Message):
    __slots__ = ("allowed_upstream_headers", "allowed_upstream_headers_to_append", "allowed_client_headers", "allowed_client_headers_on_success", "dynamic_metadata_from_headers")
    ALLOWED_UPSTREAM_HEADERS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_UPSTREAM_HEADERS_TO_APPEND_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_CLIENT_HEADERS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_CLIENT_HEADERS_ON_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_METADATA_FROM_HEADERS_FIELD_NUMBER: _ClassVar[int]
    allowed_upstream_headers: _string_pb2.ListStringMatcher
    allowed_upstream_headers_to_append: _string_pb2.ListStringMatcher
    allowed_client_headers: _string_pb2.ListStringMatcher
    allowed_client_headers_on_success: _string_pb2.ListStringMatcher
    dynamic_metadata_from_headers: _string_pb2.ListStringMatcher
    def __init__(self, allowed_upstream_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., allowed_upstream_headers_to_append: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., allowed_client_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., allowed_client_headers_on_success: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., dynamic_metadata_from_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ...) -> None: ...

class ExtAuthzPerRoute(_message.Message):
    __slots__ = ("disabled", "check_settings")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    CHECK_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    check_settings: CheckSettings
    def __init__(self, disabled: bool = ..., check_settings: _Optional[_Union[CheckSettings, _Mapping]] = ...) -> None: ...

class CheckSettings(_message.Message):
    __slots__ = ("context_extensions", "disable_request_body_buffering", "with_request_body", "grpc_service", "http_service")
    class ContextExtensionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONTEXT_EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_REQUEST_BODY_BUFFERING_FIELD_NUMBER: _ClassVar[int]
    WITH_REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    context_extensions: _containers.ScalarMap[str, str]
    disable_request_body_buffering: bool
    with_request_body: BufferSettings
    grpc_service: _grpc_service_pb2.GrpcService
    http_service: HttpService
    def __init__(self, context_extensions: _Optional[_Mapping[str, str]] = ..., disable_request_body_buffering: bool = ..., with_request_body: _Optional[_Union[BufferSettings, _Mapping]] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., http_service: _Optional[_Union[HttpService, _Mapping]] = ...) -> None: ...
