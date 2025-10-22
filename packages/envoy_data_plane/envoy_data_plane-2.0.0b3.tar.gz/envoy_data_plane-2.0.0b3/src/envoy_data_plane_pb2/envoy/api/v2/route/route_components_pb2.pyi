import datetime

from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.type.matcher import regex_pb2 as _regex_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from envoy.type import percent_pb2 as _percent_pb2
from envoy.type import range_pb2 as _range_pb2
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

class VirtualHost(_message.Message):
    __slots__ = ("name", "domains", "routes", "require_tls", "virtual_clusters", "rate_limits", "request_headers_to_add", "request_headers_to_remove", "response_headers_to_add", "response_headers_to_remove", "cors", "per_filter_config", "typed_per_filter_config", "include_request_attempt_count", "include_attempt_count_in_response", "retry_policy", "retry_policy_typed_config", "hedge_policy", "per_request_buffer_limit_bytes")
    class TlsRequirementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[VirtualHost.TlsRequirementType]
        EXTERNAL_ONLY: _ClassVar[VirtualHost.TlsRequirementType]
        ALL: _ClassVar[VirtualHost.TlsRequirementType]
    NONE: VirtualHost.TlsRequirementType
    EXTERNAL_ONLY: VirtualHost.TlsRequirementType
    ALL: VirtualHost.TlsRequirementType
    class PerFilterConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Struct
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    class TypedPerFilterConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_TLS_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    CORS_FIELD_NUMBER: _ClassVar[int]
    PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_REQUEST_ATTEMPT_COUNT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ATTEMPT_COUNT_IN_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    HEDGE_POLICY_FIELD_NUMBER: _ClassVar[int]
    PER_REQUEST_BUFFER_LIMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    domains: _containers.RepeatedScalarFieldContainer[str]
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    require_tls: VirtualHost.TlsRequirementType
    virtual_clusters: _containers.RepeatedCompositeFieldContainer[VirtualCluster]
    rate_limits: _containers.RepeatedCompositeFieldContainer[RateLimit]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    cors: CorsPolicy
    per_filter_config: _containers.MessageMap[str, _struct_pb2.Struct]
    typed_per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
    include_request_attempt_count: bool
    include_attempt_count_in_response: bool
    retry_policy: RetryPolicy
    retry_policy_typed_config: _any_pb2.Any
    hedge_policy: HedgePolicy
    per_request_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    def __init__(self, name: _Optional[str] = ..., domains: _Optional[_Iterable[str]] = ..., routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ..., require_tls: _Optional[_Union[VirtualHost.TlsRequirementType, str]] = ..., virtual_clusters: _Optional[_Iterable[_Union[VirtualCluster, _Mapping]]] = ..., rate_limits: _Optional[_Iterable[_Union[RateLimit, _Mapping]]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., cors: _Optional[_Union[CorsPolicy, _Mapping]] = ..., per_filter_config: _Optional[_Mapping[str, _struct_pb2.Struct]] = ..., typed_per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ..., include_request_attempt_count: bool = ..., include_attempt_count_in_response: bool = ..., retry_policy: _Optional[_Union[RetryPolicy, _Mapping]] = ..., retry_policy_typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., hedge_policy: _Optional[_Union[HedgePolicy, _Mapping]] = ..., per_request_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class FilterAction(_message.Message):
    __slots__ = ("action",)
    ACTION_FIELD_NUMBER: _ClassVar[int]
    action: _any_pb2.Any
    def __init__(self, action: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Route(_message.Message):
    __slots__ = ("name", "match", "route", "redirect", "direct_response", "filter_action", "metadata", "decorator", "per_filter_config", "typed_per_filter_config", "request_headers_to_add", "request_headers_to_remove", "response_headers_to_add", "response_headers_to_remove", "tracing", "per_request_buffer_limit_bytes")
    class PerFilterConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Struct
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    class TypedPerFilterConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    ROUTE_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    DIRECT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    FILTER_ACTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DECORATOR_FIELD_NUMBER: _ClassVar[int]
    PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    PER_REQUEST_BUFFER_LIMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    match: RouteMatch
    route: RouteAction
    redirect: RedirectAction
    direct_response: DirectResponseAction
    filter_action: FilterAction
    metadata: _base_pb2.Metadata
    decorator: Decorator
    per_filter_config: _containers.MessageMap[str, _struct_pb2.Struct]
    typed_per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    tracing: Tracing
    per_request_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    def __init__(self, name: _Optional[str] = ..., match: _Optional[_Union[RouteMatch, _Mapping]] = ..., route: _Optional[_Union[RouteAction, _Mapping]] = ..., redirect: _Optional[_Union[RedirectAction, _Mapping]] = ..., direct_response: _Optional[_Union[DirectResponseAction, _Mapping]] = ..., filter_action: _Optional[_Union[FilterAction, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., decorator: _Optional[_Union[Decorator, _Mapping]] = ..., per_filter_config: _Optional[_Mapping[str, _struct_pb2.Struct]] = ..., typed_per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., tracing: _Optional[_Union[Tracing, _Mapping]] = ..., per_request_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class WeightedCluster(_message.Message):
    __slots__ = ("clusters", "total_weight", "runtime_key_prefix")
    class ClusterWeight(_message.Message):
        __slots__ = ("name", "weight", "metadata_match", "request_headers_to_add", "request_headers_to_remove", "response_headers_to_add", "response_headers_to_remove", "per_filter_config", "typed_per_filter_config")
        class PerFilterConfigEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _struct_pb2.Struct
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
        class TypedPerFilterConfigEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _any_pb2.Any
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
        NAME_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
        PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
        TYPED_PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        weight: _wrappers_pb2.UInt32Value
        metadata_match: _base_pb2.Metadata
        request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
        response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
        per_filter_config: _containers.MessageMap[str, _struct_pb2.Struct]
        typed_per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
        def __init__(self, name: _Optional[str] = ..., weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., per_filter_config: _Optional[_Mapping[str, _struct_pb2.Struct]] = ..., typed_per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ...) -> None: ...
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_KEY_PREFIX_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedCompositeFieldContainer[WeightedCluster.ClusterWeight]
    total_weight: _wrappers_pb2.UInt32Value
    runtime_key_prefix: str
    def __init__(self, clusters: _Optional[_Iterable[_Union[WeightedCluster.ClusterWeight, _Mapping]]] = ..., total_weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., runtime_key_prefix: _Optional[str] = ...) -> None: ...

class RouteMatch(_message.Message):
    __slots__ = ("prefix", "path", "regex", "safe_regex", "case_sensitive", "runtime_fraction", "headers", "query_parameters", "grpc", "tls_context")
    class GrpcRouteMatchOptions(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class TlsContextMatchOptions(_message.Message):
        __slots__ = ("presented", "validated")
        PRESENTED_FIELD_NUMBER: _ClassVar[int]
        VALIDATED_FIELD_NUMBER: _ClassVar[int]
        presented: _wrappers_pb2.BoolValue
        validated: _wrappers_pb2.BoolValue
        def __init__(self, presented: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., validated: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    SAFE_REGEX_FIELD_NUMBER: _ClassVar[int]
    CASE_SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    GRPC_FIELD_NUMBER: _ClassVar[int]
    TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    prefix: str
    path: str
    regex: str
    safe_regex: _regex_pb2.RegexMatcher
    case_sensitive: _wrappers_pb2.BoolValue
    runtime_fraction: _base_pb2.RuntimeFractionalPercent
    headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    query_parameters: _containers.RepeatedCompositeFieldContainer[QueryParameterMatcher]
    grpc: RouteMatch.GrpcRouteMatchOptions
    tls_context: RouteMatch.TlsContextMatchOptions
    def __init__(self, prefix: _Optional[str] = ..., path: _Optional[str] = ..., regex: _Optional[str] = ..., safe_regex: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., case_sensitive: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ..., query_parameters: _Optional[_Iterable[_Union[QueryParameterMatcher, _Mapping]]] = ..., grpc: _Optional[_Union[RouteMatch.GrpcRouteMatchOptions, _Mapping]] = ..., tls_context: _Optional[_Union[RouteMatch.TlsContextMatchOptions, _Mapping]] = ...) -> None: ...

class CorsPolicy(_message.Message):
    __slots__ = ("allow_origin", "allow_origin_regex", "allow_origin_string_match", "allow_methods", "allow_headers", "expose_headers", "max_age", "allow_credentials", "enabled", "filter_enabled", "shadow_enabled")
    ALLOW_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    ALLOW_ORIGIN_REGEX_FIELD_NUMBER: _ClassVar[int]
    ALLOW_ORIGIN_STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    ALLOW_METHODS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_HEADERS_FIELD_NUMBER: _ClassVar[int]
    EXPOSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    MAX_AGE_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SHADOW_ENABLED_FIELD_NUMBER: _ClassVar[int]
    allow_origin: _containers.RepeatedScalarFieldContainer[str]
    allow_origin_regex: _containers.RepeatedScalarFieldContainer[str]
    allow_origin_string_match: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    allow_methods: str
    allow_headers: str
    expose_headers: str
    max_age: str
    allow_credentials: _wrappers_pb2.BoolValue
    enabled: _wrappers_pb2.BoolValue
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    shadow_enabled: _base_pb2.RuntimeFractionalPercent
    def __init__(self, allow_origin: _Optional[_Iterable[str]] = ..., allow_origin_regex: _Optional[_Iterable[str]] = ..., allow_origin_string_match: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., allow_methods: _Optional[str] = ..., allow_headers: _Optional[str] = ..., expose_headers: _Optional[str] = ..., max_age: _Optional[str] = ..., allow_credentials: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., enabled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., shadow_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ...) -> None: ...

class RouteAction(_message.Message):
    __slots__ = ("cluster", "cluster_header", "weighted_clusters", "cluster_not_found_response_code", "metadata_match", "prefix_rewrite", "regex_rewrite", "host_rewrite", "auto_host_rewrite", "auto_host_rewrite_header", "timeout", "idle_timeout", "retry_policy", "retry_policy_typed_config", "request_mirror_policy", "request_mirror_policies", "priority", "rate_limits", "include_vh_rate_limits", "hash_policy", "cors", "max_grpc_timeout", "grpc_timeout_offset", "upgrade_configs", "internal_redirect_action", "max_internal_redirects", "hedge_policy")
    class ClusterNotFoundResponseCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SERVICE_UNAVAILABLE: _ClassVar[RouteAction.ClusterNotFoundResponseCode]
        NOT_FOUND: _ClassVar[RouteAction.ClusterNotFoundResponseCode]
    SERVICE_UNAVAILABLE: RouteAction.ClusterNotFoundResponseCode
    NOT_FOUND: RouteAction.ClusterNotFoundResponseCode
    class InternalRedirectAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PASS_THROUGH_INTERNAL_REDIRECT: _ClassVar[RouteAction.InternalRedirectAction]
        HANDLE_INTERNAL_REDIRECT: _ClassVar[RouteAction.InternalRedirectAction]
    PASS_THROUGH_INTERNAL_REDIRECT: RouteAction.InternalRedirectAction
    HANDLE_INTERNAL_REDIRECT: RouteAction.InternalRedirectAction
    class RequestMirrorPolicy(_message.Message):
        __slots__ = ("cluster", "runtime_key", "runtime_fraction", "trace_sampled")
        CLUSTER_FIELD_NUMBER: _ClassVar[int]
        RUNTIME_KEY_FIELD_NUMBER: _ClassVar[int]
        RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
        TRACE_SAMPLED_FIELD_NUMBER: _ClassVar[int]
        cluster: str
        runtime_key: str
        runtime_fraction: _base_pb2.RuntimeFractionalPercent
        trace_sampled: _wrappers_pb2.BoolValue
        def __init__(self, cluster: _Optional[str] = ..., runtime_key: _Optional[str] = ..., runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., trace_sampled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    class HashPolicy(_message.Message):
        __slots__ = ("header", "cookie", "connection_properties", "query_parameter", "filter_state", "terminal")
        class Header(_message.Message):
            __slots__ = ("header_name",)
            HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
            header_name: str
            def __init__(self, header_name: _Optional[str] = ...) -> None: ...
        class Cookie(_message.Message):
            __slots__ = ("name", "ttl", "path")
            NAME_FIELD_NUMBER: _ClassVar[int]
            TTL_FIELD_NUMBER: _ClassVar[int]
            PATH_FIELD_NUMBER: _ClassVar[int]
            name: str
            ttl: _duration_pb2.Duration
            path: str
            def __init__(self, name: _Optional[str] = ..., ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., path: _Optional[str] = ...) -> None: ...
        class ConnectionProperties(_message.Message):
            __slots__ = ("source_ip",)
            SOURCE_IP_FIELD_NUMBER: _ClassVar[int]
            source_ip: bool
            def __init__(self, source_ip: bool = ...) -> None: ...
        class QueryParameter(_message.Message):
            __slots__ = ("name",)
            NAME_FIELD_NUMBER: _ClassVar[int]
            name: str
            def __init__(self, name: _Optional[str] = ...) -> None: ...
        class FilterState(_message.Message):
            __slots__ = ("key",)
            KEY_FIELD_NUMBER: _ClassVar[int]
            key: str
            def __init__(self, key: _Optional[str] = ...) -> None: ...
        HEADER_FIELD_NUMBER: _ClassVar[int]
        COOKIE_FIELD_NUMBER: _ClassVar[int]
        CONNECTION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        QUERY_PARAMETER_FIELD_NUMBER: _ClassVar[int]
        FILTER_STATE_FIELD_NUMBER: _ClassVar[int]
        TERMINAL_FIELD_NUMBER: _ClassVar[int]
        header: RouteAction.HashPolicy.Header
        cookie: RouteAction.HashPolicy.Cookie
        connection_properties: RouteAction.HashPolicy.ConnectionProperties
        query_parameter: RouteAction.HashPolicy.QueryParameter
        filter_state: RouteAction.HashPolicy.FilterState
        terminal: bool
        def __init__(self, header: _Optional[_Union[RouteAction.HashPolicy.Header, _Mapping]] = ..., cookie: _Optional[_Union[RouteAction.HashPolicy.Cookie, _Mapping]] = ..., connection_properties: _Optional[_Union[RouteAction.HashPolicy.ConnectionProperties, _Mapping]] = ..., query_parameter: _Optional[_Union[RouteAction.HashPolicy.QueryParameter, _Mapping]] = ..., filter_state: _Optional[_Union[RouteAction.HashPolicy.FilterState, _Mapping]] = ..., terminal: bool = ...) -> None: ...
    class UpgradeConfig(_message.Message):
        __slots__ = ("upgrade_type", "enabled")
        UPGRADE_TYPE_FIELD_NUMBER: _ClassVar[int]
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        upgrade_type: str
        enabled: _wrappers_pb2.BoolValue
        def __init__(self, upgrade_type: _Optional[str] = ..., enabled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_HEADER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NOT_FOUND_RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    PREFIX_REWRITE_FIELD_NUMBER: _ClassVar[int]
    REGEX_REWRITE_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    AUTO_HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    AUTO_HOST_REWRITE_HEADER_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MIRROR_POLICY_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MIRROR_POLICIES_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_VH_RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    HASH_POLICY_FIELD_NUMBER: _ClassVar[int]
    CORS_FIELD_NUMBER: _ClassVar[int]
    MAX_GRPC_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    GRPC_TIMEOUT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    UPGRADE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REDIRECT_ACTION_FIELD_NUMBER: _ClassVar[int]
    MAX_INTERNAL_REDIRECTS_FIELD_NUMBER: _ClassVar[int]
    HEDGE_POLICY_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    cluster_header: str
    weighted_clusters: WeightedCluster
    cluster_not_found_response_code: RouteAction.ClusterNotFoundResponseCode
    metadata_match: _base_pb2.Metadata
    prefix_rewrite: str
    regex_rewrite: _regex_pb2.RegexMatchAndSubstitute
    host_rewrite: str
    auto_host_rewrite: _wrappers_pb2.BoolValue
    auto_host_rewrite_header: str
    timeout: _duration_pb2.Duration
    idle_timeout: _duration_pb2.Duration
    retry_policy: RetryPolicy
    retry_policy_typed_config: _any_pb2.Any
    request_mirror_policy: RouteAction.RequestMirrorPolicy
    request_mirror_policies: _containers.RepeatedCompositeFieldContainer[RouteAction.RequestMirrorPolicy]
    priority: _base_pb2.RoutingPriority
    rate_limits: _containers.RepeatedCompositeFieldContainer[RateLimit]
    include_vh_rate_limits: _wrappers_pb2.BoolValue
    hash_policy: _containers.RepeatedCompositeFieldContainer[RouteAction.HashPolicy]
    cors: CorsPolicy
    max_grpc_timeout: _duration_pb2.Duration
    grpc_timeout_offset: _duration_pb2.Duration
    upgrade_configs: _containers.RepeatedCompositeFieldContainer[RouteAction.UpgradeConfig]
    internal_redirect_action: RouteAction.InternalRedirectAction
    max_internal_redirects: _wrappers_pb2.UInt32Value
    hedge_policy: HedgePolicy
    def __init__(self, cluster: _Optional[str] = ..., cluster_header: _Optional[str] = ..., weighted_clusters: _Optional[_Union[WeightedCluster, _Mapping]] = ..., cluster_not_found_response_code: _Optional[_Union[RouteAction.ClusterNotFoundResponseCode, str]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., prefix_rewrite: _Optional[str] = ..., regex_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., host_rewrite: _Optional[str] = ..., auto_host_rewrite: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., auto_host_rewrite_header: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., retry_policy: _Optional[_Union[RetryPolicy, _Mapping]] = ..., retry_policy_typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., request_mirror_policy: _Optional[_Union[RouteAction.RequestMirrorPolicy, _Mapping]] = ..., request_mirror_policies: _Optional[_Iterable[_Union[RouteAction.RequestMirrorPolicy, _Mapping]]] = ..., priority: _Optional[_Union[_base_pb2.RoutingPriority, str]] = ..., rate_limits: _Optional[_Iterable[_Union[RateLimit, _Mapping]]] = ..., include_vh_rate_limits: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., hash_policy: _Optional[_Iterable[_Union[RouteAction.HashPolicy, _Mapping]]] = ..., cors: _Optional[_Union[CorsPolicy, _Mapping]] = ..., max_grpc_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., grpc_timeout_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upgrade_configs: _Optional[_Iterable[_Union[RouteAction.UpgradeConfig, _Mapping]]] = ..., internal_redirect_action: _Optional[_Union[RouteAction.InternalRedirectAction, str]] = ..., max_internal_redirects: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., hedge_policy: _Optional[_Union[HedgePolicy, _Mapping]] = ...) -> None: ...

class RetryPolicy(_message.Message):
    __slots__ = ("retry_on", "num_retries", "per_try_timeout", "retry_priority", "retry_host_predicate", "host_selection_retry_max_attempts", "retriable_status_codes", "retry_back_off", "retriable_headers", "retriable_request_headers")
    class RetryPriority(_message.Message):
        __slots__ = ("name", "config", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CONFIG_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        config: _struct_pb2.Struct
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class RetryHostPredicate(_message.Message):
        __slots__ = ("name", "config", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CONFIG_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        config: _struct_pb2.Struct
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class RetryBackOff(_message.Message):
        __slots__ = ("base_interval", "max_interval")
        BASE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        MAX_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        base_interval: _duration_pb2.Duration
        max_interval: _duration_pb2.Duration
        def __init__(self, base_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    RETRY_ON_FIELD_NUMBER: _ClassVar[int]
    NUM_RETRIES_FIELD_NUMBER: _ClassVar[int]
    PER_TRY_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    RETRY_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    RETRY_HOST_PREDICATE_FIELD_NUMBER: _ClassVar[int]
    HOST_SELECTION_RETRY_MAX_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    RETRIABLE_STATUS_CODES_FIELD_NUMBER: _ClassVar[int]
    RETRY_BACK_OFF_FIELD_NUMBER: _ClassVar[int]
    RETRIABLE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RETRIABLE_REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    retry_on: str
    num_retries: _wrappers_pb2.UInt32Value
    per_try_timeout: _duration_pb2.Duration
    retry_priority: RetryPolicy.RetryPriority
    retry_host_predicate: _containers.RepeatedCompositeFieldContainer[RetryPolicy.RetryHostPredicate]
    host_selection_retry_max_attempts: int
    retriable_status_codes: _containers.RepeatedScalarFieldContainer[int]
    retry_back_off: RetryPolicy.RetryBackOff
    retriable_headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    retriable_request_headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    def __init__(self, retry_on: _Optional[str] = ..., num_retries: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., per_try_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., retry_priority: _Optional[_Union[RetryPolicy.RetryPriority, _Mapping]] = ..., retry_host_predicate: _Optional[_Iterable[_Union[RetryPolicy.RetryHostPredicate, _Mapping]]] = ..., host_selection_retry_max_attempts: _Optional[int] = ..., retriable_status_codes: _Optional[_Iterable[int]] = ..., retry_back_off: _Optional[_Union[RetryPolicy.RetryBackOff, _Mapping]] = ..., retriable_headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ..., retriable_request_headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ...) -> None: ...

class HedgePolicy(_message.Message):
    __slots__ = ("initial_requests", "additional_request_chance", "hedge_on_per_try_timeout")
    INITIAL_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_REQUEST_CHANCE_FIELD_NUMBER: _ClassVar[int]
    HEDGE_ON_PER_TRY_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    initial_requests: _wrappers_pb2.UInt32Value
    additional_request_chance: _percent_pb2.FractionalPercent
    hedge_on_per_try_timeout: bool
    def __init__(self, initial_requests: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., additional_request_chance: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., hedge_on_per_try_timeout: bool = ...) -> None: ...

class RedirectAction(_message.Message):
    __slots__ = ("https_redirect", "scheme_redirect", "host_redirect", "port_redirect", "path_redirect", "prefix_rewrite", "response_code", "strip_query")
    class RedirectResponseCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MOVED_PERMANENTLY: _ClassVar[RedirectAction.RedirectResponseCode]
        FOUND: _ClassVar[RedirectAction.RedirectResponseCode]
        SEE_OTHER: _ClassVar[RedirectAction.RedirectResponseCode]
        TEMPORARY_REDIRECT: _ClassVar[RedirectAction.RedirectResponseCode]
        PERMANENT_REDIRECT: _ClassVar[RedirectAction.RedirectResponseCode]
    MOVED_PERMANENTLY: RedirectAction.RedirectResponseCode
    FOUND: RedirectAction.RedirectResponseCode
    SEE_OTHER: RedirectAction.RedirectResponseCode
    TEMPORARY_REDIRECT: RedirectAction.RedirectResponseCode
    PERMANENT_REDIRECT: RedirectAction.RedirectResponseCode
    HTTPS_REDIRECT_FIELD_NUMBER: _ClassVar[int]
    SCHEME_REDIRECT_FIELD_NUMBER: _ClassVar[int]
    HOST_REDIRECT_FIELD_NUMBER: _ClassVar[int]
    PORT_REDIRECT_FIELD_NUMBER: _ClassVar[int]
    PATH_REDIRECT_FIELD_NUMBER: _ClassVar[int]
    PREFIX_REWRITE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    STRIP_QUERY_FIELD_NUMBER: _ClassVar[int]
    https_redirect: bool
    scheme_redirect: str
    host_redirect: str
    port_redirect: int
    path_redirect: str
    prefix_rewrite: str
    response_code: RedirectAction.RedirectResponseCode
    strip_query: bool
    def __init__(self, https_redirect: bool = ..., scheme_redirect: _Optional[str] = ..., host_redirect: _Optional[str] = ..., port_redirect: _Optional[int] = ..., path_redirect: _Optional[str] = ..., prefix_rewrite: _Optional[str] = ..., response_code: _Optional[_Union[RedirectAction.RedirectResponseCode, str]] = ..., strip_query: bool = ...) -> None: ...

class DirectResponseAction(_message.Message):
    __slots__ = ("status", "body")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    status: int
    body: _base_pb2.DataSource
    def __init__(self, status: _Optional[int] = ..., body: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...

class Decorator(_message.Message):
    __slots__ = ("operation", "propagate")
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    PROPAGATE_FIELD_NUMBER: _ClassVar[int]
    operation: str
    propagate: _wrappers_pb2.BoolValue
    def __init__(self, operation: _Optional[str] = ..., propagate: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class Tracing(_message.Message):
    __slots__ = ("client_sampling", "random_sampling", "overall_sampling", "custom_tags")
    CLIENT_SAMPLING_FIELD_NUMBER: _ClassVar[int]
    RANDOM_SAMPLING_FIELD_NUMBER: _ClassVar[int]
    OVERALL_SAMPLING_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
    client_sampling: _percent_pb2.FractionalPercent
    random_sampling: _percent_pb2.FractionalPercent
    overall_sampling: _percent_pb2.FractionalPercent
    custom_tags: _containers.RepeatedCompositeFieldContainer[_custom_tag_pb2.CustomTag]
    def __init__(self, client_sampling: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., random_sampling: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., overall_sampling: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., custom_tags: _Optional[_Iterable[_Union[_custom_tag_pb2.CustomTag, _Mapping]]] = ...) -> None: ...

class VirtualCluster(_message.Message):
    __slots__ = ("pattern", "headers", "name", "method")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    name: str
    method: _base_pb2.RequestMethod
    def __init__(self, pattern: _Optional[str] = ..., headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ..., name: _Optional[str] = ..., method: _Optional[_Union[_base_pb2.RequestMethod, str]] = ...) -> None: ...

class RateLimit(_message.Message):
    __slots__ = ("stage", "disable_key", "actions")
    class Action(_message.Message):
        __slots__ = ("source_cluster", "destination_cluster", "request_headers", "remote_address", "generic_key", "header_value_match")
        class SourceCluster(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class DestinationCluster(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class RequestHeaders(_message.Message):
            __slots__ = ("header_name", "descriptor_key")
            HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            header_name: str
            descriptor_key: str
            def __init__(self, header_name: _Optional[str] = ..., descriptor_key: _Optional[str] = ...) -> None: ...
        class RemoteAddress(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class GenericKey(_message.Message):
            __slots__ = ("descriptor_value",)
            DESCRIPTOR_VALUE_FIELD_NUMBER: _ClassVar[int]
            descriptor_value: str
            def __init__(self, descriptor_value: _Optional[str] = ...) -> None: ...
        class HeaderValueMatch(_message.Message):
            __slots__ = ("descriptor_value", "expect_match", "headers")
            DESCRIPTOR_VALUE_FIELD_NUMBER: _ClassVar[int]
            EXPECT_MATCH_FIELD_NUMBER: _ClassVar[int]
            HEADERS_FIELD_NUMBER: _ClassVar[int]
            descriptor_value: str
            expect_match: _wrappers_pb2.BoolValue
            headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
            def __init__(self, descriptor_value: _Optional[str] = ..., expect_match: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ...) -> None: ...
        SOURCE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
        DESTINATION_CLUSTER_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
        REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        GENERIC_KEY_FIELD_NUMBER: _ClassVar[int]
        HEADER_VALUE_MATCH_FIELD_NUMBER: _ClassVar[int]
        source_cluster: RateLimit.Action.SourceCluster
        destination_cluster: RateLimit.Action.DestinationCluster
        request_headers: RateLimit.Action.RequestHeaders
        remote_address: RateLimit.Action.RemoteAddress
        generic_key: RateLimit.Action.GenericKey
        header_value_match: RateLimit.Action.HeaderValueMatch
        def __init__(self, source_cluster: _Optional[_Union[RateLimit.Action.SourceCluster, _Mapping]] = ..., destination_cluster: _Optional[_Union[RateLimit.Action.DestinationCluster, _Mapping]] = ..., request_headers: _Optional[_Union[RateLimit.Action.RequestHeaders, _Mapping]] = ..., remote_address: _Optional[_Union[RateLimit.Action.RemoteAddress, _Mapping]] = ..., generic_key: _Optional[_Union[RateLimit.Action.GenericKey, _Mapping]] = ..., header_value_match: _Optional[_Union[RateLimit.Action.HeaderValueMatch, _Mapping]] = ...) -> None: ...
    STAGE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_KEY_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    stage: _wrappers_pb2.UInt32Value
    disable_key: str
    actions: _containers.RepeatedCompositeFieldContainer[RateLimit.Action]
    def __init__(self, stage: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., disable_key: _Optional[str] = ..., actions: _Optional[_Iterable[_Union[RateLimit.Action, _Mapping]]] = ...) -> None: ...

class HeaderMatcher(_message.Message):
    __slots__ = ("name", "exact_match", "regex_match", "safe_regex_match", "range_match", "present_match", "prefix_match", "suffix_match", "invert_match")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXACT_MATCH_FIELD_NUMBER: _ClassVar[int]
    REGEX_MATCH_FIELD_NUMBER: _ClassVar[int]
    SAFE_REGEX_MATCH_FIELD_NUMBER: _ClassVar[int]
    RANGE_MATCH_FIELD_NUMBER: _ClassVar[int]
    PRESENT_MATCH_FIELD_NUMBER: _ClassVar[int]
    PREFIX_MATCH_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_MATCH_FIELD_NUMBER: _ClassVar[int]
    INVERT_MATCH_FIELD_NUMBER: _ClassVar[int]
    name: str
    exact_match: str
    regex_match: str
    safe_regex_match: _regex_pb2.RegexMatcher
    range_match: _range_pb2.Int64Range
    present_match: bool
    prefix_match: str
    suffix_match: str
    invert_match: bool
    def __init__(self, name: _Optional[str] = ..., exact_match: _Optional[str] = ..., regex_match: _Optional[str] = ..., safe_regex_match: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., range_match: _Optional[_Union[_range_pb2.Int64Range, _Mapping]] = ..., present_match: bool = ..., prefix_match: _Optional[str] = ..., suffix_match: _Optional[str] = ..., invert_match: bool = ...) -> None: ...

class QueryParameterMatcher(_message.Message):
    __slots__ = ("name", "value", "regex", "string_match", "present_match")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    PRESENT_MATCH_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    regex: _wrappers_pb2.BoolValue
    string_match: _string_pb2.StringMatcher
    present_match: bool
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., regex: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., string_match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., present_match: bool = ...) -> None: ...
