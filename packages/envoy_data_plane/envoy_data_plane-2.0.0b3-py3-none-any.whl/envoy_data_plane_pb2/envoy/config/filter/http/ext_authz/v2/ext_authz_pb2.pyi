from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import grpc_service_pb2 as _grpc_service_pb2
from envoy.api.v2.core import http_uri_pb2 as _http_uri_pb2
from envoy.type import http_status_pb2 as _http_status_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtAuthz(_message.Message):
    __slots__ = ("grpc_service", "http_service", "failure_mode_allow", "use_alpha", "with_request_body", "clear_route_cache", "status_on_error", "metadata_context_namespaces", "filter_enabled", "deny_at_disable", "include_peer_certificate")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    USE_ALPHA_FIELD_NUMBER: _ClassVar[int]
    WITH_REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    CLEAR_ROUTE_CACHE_FIELD_NUMBER: _ClassVar[int]
    STATUS_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    METADATA_CONTEXT_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    DENY_AT_DISABLE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PEER_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    http_service: HttpService
    failure_mode_allow: bool
    use_alpha: bool
    with_request_body: BufferSettings
    clear_route_cache: bool
    status_on_error: _http_status_pb2.HttpStatus
    metadata_context_namespaces: _containers.RepeatedScalarFieldContainer[str]
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    deny_at_disable: _base_pb2.RuntimeFeatureFlag
    include_peer_certificate: bool
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., http_service: _Optional[_Union[HttpService, _Mapping]] = ..., failure_mode_allow: bool = ..., use_alpha: bool = ..., with_request_body: _Optional[_Union[BufferSettings, _Mapping]] = ..., clear_route_cache: bool = ..., status_on_error: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., metadata_context_namespaces: _Optional[_Iterable[str]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., deny_at_disable: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., include_peer_certificate: bool = ...) -> None: ...

class BufferSettings(_message.Message):
    __slots__ = ("max_request_bytes", "allow_partial_message")
    MAX_REQUEST_BYTES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    max_request_bytes: int
    allow_partial_message: bool
    def __init__(self, max_request_bytes: _Optional[int] = ..., allow_partial_message: bool = ...) -> None: ...

class HttpService(_message.Message):
    __slots__ = ("server_uri", "path_prefix", "authorization_request", "authorization_response")
    SERVER_URI_FIELD_NUMBER: _ClassVar[int]
    PATH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    server_uri: _http_uri_pb2.HttpUri
    path_prefix: str
    authorization_request: AuthorizationRequest
    authorization_response: AuthorizationResponse
    def __init__(self, server_uri: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., path_prefix: _Optional[str] = ..., authorization_request: _Optional[_Union[AuthorizationRequest, _Mapping]] = ..., authorization_response: _Optional[_Union[AuthorizationResponse, _Mapping]] = ...) -> None: ...

class AuthorizationRequest(_message.Message):
    __slots__ = ("allowed_headers", "headers_to_add")
    ALLOWED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    allowed_headers: _string_pb2.ListStringMatcher
    headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
    def __init__(self, allowed_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ...) -> None: ...

class AuthorizationResponse(_message.Message):
    __slots__ = ("allowed_upstream_headers", "allowed_client_headers")
    ALLOWED_UPSTREAM_HEADERS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_CLIENT_HEADERS_FIELD_NUMBER: _ClassVar[int]
    allowed_upstream_headers: _string_pb2.ListStringMatcher
    allowed_client_headers: _string_pb2.ListStringMatcher
    def __init__(self, allowed_upstream_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., allowed_client_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ...) -> None: ...

class ExtAuthzPerRoute(_message.Message):
    __slots__ = ("disabled", "check_settings")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    CHECK_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    check_settings: CheckSettings
    def __init__(self, disabled: bool = ..., check_settings: _Optional[_Union[CheckSettings, _Mapping]] = ...) -> None: ...

class CheckSettings(_message.Message):
    __slots__ = ("context_extensions",)
    class ContextExtensionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONTEXT_EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    context_extensions: _containers.ScalarMap[str, str]
    def __init__(self, context_extensions: _Optional[_Mapping[str, str]] = ...) -> None: ...
