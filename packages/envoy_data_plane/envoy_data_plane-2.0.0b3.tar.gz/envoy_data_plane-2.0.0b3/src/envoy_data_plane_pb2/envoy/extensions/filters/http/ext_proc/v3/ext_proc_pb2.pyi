import datetime

from envoy.config.common.mutation_rules.v3 import mutation_rules_pb2 as _mutation_rules_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.config.core.v3 import http_service_pb2 as _http_service_pb2
from envoy.extensions.filters.http.ext_proc.v3 import processing_mode_pb2 as _processing_mode_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExternalProcessor(_message.Message):
    __slots__ = ("grpc_service", "http_service", "failure_mode_allow", "processing_mode", "request_attributes", "response_attributes", "message_timeout", "stat_prefix", "mutation_rules", "max_message_timeout", "forward_rules", "filter_metadata", "allow_mode_override", "disable_immediate_response", "metadata_options", "observability_mode", "disable_clear_route_cache", "route_cache_action", "deferred_close_timeout", "send_body_without_waiting_for_header_response", "allowed_override_modes", "processing_request_modifier", "on_processing_response", "status_on_error")
    class RouteCacheAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[ExternalProcessor.RouteCacheAction]
        CLEAR: _ClassVar[ExternalProcessor.RouteCacheAction]
        RETAIN: _ClassVar[ExternalProcessor.RouteCacheAction]
    DEFAULT: ExternalProcessor.RouteCacheAction
    CLEAR: ExternalProcessor.RouteCacheAction
    RETAIN: ExternalProcessor.RouteCacheAction
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_MODE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    MUTATION_RULES_FIELD_NUMBER: _ClassVar[int]
    MAX_MESSAGE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FORWARD_RULES_FIELD_NUMBER: _ClassVar[int]
    FILTER_METADATA_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MODE_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_IMMEDIATE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    METADATA_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    OBSERVABILITY_MODE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_CLEAR_ROUTE_CACHE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CACHE_ACTION_FIELD_NUMBER: _ClassVar[int]
    DEFERRED_CLOSE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SEND_BODY_WITHOUT_WAITING_FOR_HEADER_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_OVERRIDE_MODES_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_REQUEST_MODIFIER_FIELD_NUMBER: _ClassVar[int]
    ON_PROCESSING_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    STATUS_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    http_service: ExtProcHttpService
    failure_mode_allow: bool
    processing_mode: _processing_mode_pb2.ProcessingMode
    request_attributes: _containers.RepeatedScalarFieldContainer[str]
    response_attributes: _containers.RepeatedScalarFieldContainer[str]
    message_timeout: _duration_pb2.Duration
    stat_prefix: str
    mutation_rules: _mutation_rules_pb2.HeaderMutationRules
    max_message_timeout: _duration_pb2.Duration
    forward_rules: HeaderForwardingRules
    filter_metadata: _struct_pb2.Struct
    allow_mode_override: bool
    disable_immediate_response: bool
    metadata_options: MetadataOptions
    observability_mode: bool
    disable_clear_route_cache: bool
    route_cache_action: ExternalProcessor.RouteCacheAction
    deferred_close_timeout: _duration_pb2.Duration
    send_body_without_waiting_for_header_response: bool
    allowed_override_modes: _containers.RepeatedCompositeFieldContainer[_processing_mode_pb2.ProcessingMode]
    processing_request_modifier: _extension_pb2.TypedExtensionConfig
    on_processing_response: _extension_pb2.TypedExtensionConfig
    status_on_error: _http_status_pb2.HttpStatus
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., http_service: _Optional[_Union[ExtProcHttpService, _Mapping]] = ..., failure_mode_allow: bool = ..., processing_mode: _Optional[_Union[_processing_mode_pb2.ProcessingMode, _Mapping]] = ..., request_attributes: _Optional[_Iterable[str]] = ..., response_attributes: _Optional[_Iterable[str]] = ..., message_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., mutation_rules: _Optional[_Union[_mutation_rules_pb2.HeaderMutationRules, _Mapping]] = ..., max_message_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., forward_rules: _Optional[_Union[HeaderForwardingRules, _Mapping]] = ..., filter_metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., allow_mode_override: bool = ..., disable_immediate_response: bool = ..., metadata_options: _Optional[_Union[MetadataOptions, _Mapping]] = ..., observability_mode: bool = ..., disable_clear_route_cache: bool = ..., route_cache_action: _Optional[_Union[ExternalProcessor.RouteCacheAction, str]] = ..., deferred_close_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., send_body_without_waiting_for_header_response: bool = ..., allowed_override_modes: _Optional[_Iterable[_Union[_processing_mode_pb2.ProcessingMode, _Mapping]]] = ..., processing_request_modifier: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., on_processing_response: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., status_on_error: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ...) -> None: ...

class ExtProcHttpService(_message.Message):
    __slots__ = ("http_service",)
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    http_service: _http_service_pb2.HttpService
    def __init__(self, http_service: _Optional[_Union[_http_service_pb2.HttpService, _Mapping]] = ...) -> None: ...

class MetadataOptions(_message.Message):
    __slots__ = ("forwarding_namespaces", "receiving_namespaces")
    class MetadataNamespaces(_message.Message):
        __slots__ = ("untyped", "typed")
        UNTYPED_FIELD_NUMBER: _ClassVar[int]
        TYPED_FIELD_NUMBER: _ClassVar[int]
        untyped: _containers.RepeatedScalarFieldContainer[str]
        typed: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, untyped: _Optional[_Iterable[str]] = ..., typed: _Optional[_Iterable[str]] = ...) -> None: ...
    FORWARDING_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    RECEIVING_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    forwarding_namespaces: MetadataOptions.MetadataNamespaces
    receiving_namespaces: MetadataOptions.MetadataNamespaces
    def __init__(self, forwarding_namespaces: _Optional[_Union[MetadataOptions.MetadataNamespaces, _Mapping]] = ..., receiving_namespaces: _Optional[_Union[MetadataOptions.MetadataNamespaces, _Mapping]] = ...) -> None: ...

class HeaderForwardingRules(_message.Message):
    __slots__ = ("allowed_headers", "disallowed_headers")
    ALLOWED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    DISALLOWED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    allowed_headers: _string_pb2.ListStringMatcher
    disallowed_headers: _string_pb2.ListStringMatcher
    def __init__(self, allowed_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., disallowed_headers: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ...) -> None: ...

class ExtProcPerRoute(_message.Message):
    __slots__ = ("disabled", "overrides")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    overrides: ExtProcOverrides
    def __init__(self, disabled: bool = ..., overrides: _Optional[_Union[ExtProcOverrides, _Mapping]] = ...) -> None: ...

class ExtProcOverrides(_message.Message):
    __slots__ = ("processing_mode", "async_mode", "request_attributes", "response_attributes", "grpc_service", "metadata_options", "grpc_initial_metadata", "failure_mode_allow", "processing_request_modifier")
    PROCESSING_MODE_FIELD_NUMBER: _ClassVar[int]
    ASYNC_MODE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    METADATA_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    GRPC_INITIAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_REQUEST_MODIFIER_FIELD_NUMBER: _ClassVar[int]
    processing_mode: _processing_mode_pb2.ProcessingMode
    async_mode: bool
    request_attributes: _containers.RepeatedScalarFieldContainer[str]
    response_attributes: _containers.RepeatedScalarFieldContainer[str]
    grpc_service: _grpc_service_pb2.GrpcService
    metadata_options: MetadataOptions
    grpc_initial_metadata: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
    failure_mode_allow: _wrappers_pb2.BoolValue
    processing_request_modifier: _extension_pb2.TypedExtensionConfig
    def __init__(self, processing_mode: _Optional[_Union[_processing_mode_pb2.ProcessingMode, _Mapping]] = ..., async_mode: bool = ..., request_attributes: _Optional[_Iterable[str]] = ..., response_attributes: _Optional[_Iterable[str]] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., metadata_options: _Optional[_Union[MetadataOptions, _Mapping]] = ..., grpc_initial_metadata: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ..., failure_mode_allow: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., processing_request_modifier: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
