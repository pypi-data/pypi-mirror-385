import datetime

from envoy.config.common.mutation_rules.v3 import mutation_rules_pb2 as _mutation_rules_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import proxy_protocol_pb2 as _proxy_protocol_pb2
from envoy.type.matcher.v3 import filter_state_pb2 as _filter_state_pb2
from envoy.type.matcher.v3 import metadata_pb2 as _metadata_pb2
from envoy.type.matcher.v3 import regex_pb2 as _regex_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from envoy.type.metadata.v3 import metadata_pb2 as _metadata_pb2_1
from envoy.type.tracing.v3 import custom_tag_pb2 as _custom_tag_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from envoy.type.v3 import range_pb2 as _range_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
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

class VirtualHost(_message.Message):
    __slots__ = ("name", "domains", "routes", "matcher", "require_tls", "virtual_clusters", "rate_limits", "request_headers_to_add", "request_headers_to_remove", "response_headers_to_add", "response_headers_to_remove", "cors", "typed_per_filter_config", "include_request_attempt_count", "include_attempt_count_in_response", "retry_policy", "retry_policy_typed_config", "hedge_policy", "include_is_timeout_retry_header", "per_request_buffer_limit_bytes", "request_body_buffer_limit", "request_mirror_policies", "metadata")
    class TlsRequirementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[VirtualHost.TlsRequirementType]
        EXTERNAL_ONLY: _ClassVar[VirtualHost.TlsRequirementType]
        ALL: _ClassVar[VirtualHost.TlsRequirementType]
    NONE: VirtualHost.TlsRequirementType
    EXTERNAL_ONLY: VirtualHost.TlsRequirementType
    ALL: VirtualHost.TlsRequirementType
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
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_TLS_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    CORS_FIELD_NUMBER: _ClassVar[int]
    TYPED_PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_REQUEST_ATTEMPT_COUNT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ATTEMPT_COUNT_IN_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    HEDGE_POLICY_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_IS_TIMEOUT_RETRY_HEADER_FIELD_NUMBER: _ClassVar[int]
    PER_REQUEST_BUFFER_LIMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_BODY_BUFFER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MIRROR_POLICIES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    domains: _containers.RepeatedScalarFieldContainer[str]
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    matcher: _matcher_pb2.Matcher
    require_tls: VirtualHost.TlsRequirementType
    virtual_clusters: _containers.RepeatedCompositeFieldContainer[VirtualCluster]
    rate_limits: _containers.RepeatedCompositeFieldContainer[RateLimit]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    cors: CorsPolicy
    typed_per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
    include_request_attempt_count: bool
    include_attempt_count_in_response: bool
    retry_policy: RetryPolicy
    retry_policy_typed_config: _any_pb2.Any
    hedge_policy: HedgePolicy
    include_is_timeout_retry_header: bool
    per_request_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    request_body_buffer_limit: _wrappers_pb2.UInt64Value
    request_mirror_policies: _containers.RepeatedCompositeFieldContainer[RouteAction.RequestMirrorPolicy]
    metadata: _base_pb2.Metadata
    def __init__(self, name: _Optional[str] = ..., domains: _Optional[_Iterable[str]] = ..., routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ..., matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., require_tls: _Optional[_Union[VirtualHost.TlsRequirementType, str]] = ..., virtual_clusters: _Optional[_Iterable[_Union[VirtualCluster, _Mapping]]] = ..., rate_limits: _Optional[_Iterable[_Union[RateLimit, _Mapping]]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., cors: _Optional[_Union[CorsPolicy, _Mapping]] = ..., typed_per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ..., include_request_attempt_count: bool = ..., include_attempt_count_in_response: bool = ..., retry_policy: _Optional[_Union[RetryPolicy, _Mapping]] = ..., retry_policy_typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., hedge_policy: _Optional[_Union[HedgePolicy, _Mapping]] = ..., include_is_timeout_retry_header: bool = ..., per_request_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., request_body_buffer_limit: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., request_mirror_policies: _Optional[_Iterable[_Union[RouteAction.RequestMirrorPolicy, _Mapping]]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...

class FilterAction(_message.Message):
    __slots__ = ("action",)
    ACTION_FIELD_NUMBER: _ClassVar[int]
    action: _any_pb2.Any
    def __init__(self, action: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class RouteList(_message.Message):
    __slots__ = ("routes",)
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    def __init__(self, routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ...) -> None: ...

class Route(_message.Message):
    __slots__ = ("name", "match", "route", "redirect", "direct_response", "filter_action", "non_forwarding_action", "metadata", "decorator", "typed_per_filter_config", "request_headers_to_add", "request_headers_to_remove", "response_headers_to_add", "response_headers_to_remove", "tracing", "per_request_buffer_limit_bytes", "stat_prefix", "request_body_buffer_limit")
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
    NON_FORWARDING_ACTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DECORATOR_FIELD_NUMBER: _ClassVar[int]
    TYPED_PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    PER_REQUEST_BUFFER_LIMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    REQUEST_BODY_BUFFER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    name: str
    match: RouteMatch
    route: RouteAction
    redirect: RedirectAction
    direct_response: DirectResponseAction
    filter_action: FilterAction
    non_forwarding_action: NonForwardingAction
    metadata: _base_pb2.Metadata
    decorator: Decorator
    typed_per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    tracing: Tracing
    per_request_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    stat_prefix: str
    request_body_buffer_limit: _wrappers_pb2.UInt64Value
    def __init__(self, name: _Optional[str] = ..., match: _Optional[_Union[RouteMatch, _Mapping]] = ..., route: _Optional[_Union[RouteAction, _Mapping]] = ..., redirect: _Optional[_Union[RedirectAction, _Mapping]] = ..., direct_response: _Optional[_Union[DirectResponseAction, _Mapping]] = ..., filter_action: _Optional[_Union[FilterAction, _Mapping]] = ..., non_forwarding_action: _Optional[_Union[NonForwardingAction, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., decorator: _Optional[_Union[Decorator, _Mapping]] = ..., typed_per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., tracing: _Optional[_Union[Tracing, _Mapping]] = ..., per_request_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., request_body_buffer_limit: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...

class WeightedCluster(_message.Message):
    __slots__ = ("clusters", "total_weight", "runtime_key_prefix", "header_name", "use_hash_policy")
    class ClusterWeight(_message.Message):
        __slots__ = ("name", "cluster_header", "weight", "metadata_match", "request_headers_to_add", "request_headers_to_remove", "response_headers_to_add", "response_headers_to_remove", "typed_per_filter_config", "host_rewrite_literal")
        class TypedPerFilterConfigEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _any_pb2.Any
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
        NAME_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_HEADER_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
        TYPED_PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
        HOST_REWRITE_LITERAL_FIELD_NUMBER: _ClassVar[int]
        name: str
        cluster_header: str
        weight: _wrappers_pb2.UInt32Value
        metadata_match: _base_pb2.Metadata
        request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
        response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
        typed_per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
        host_rewrite_literal: str
        def __init__(self, name: _Optional[str] = ..., cluster_header: _Optional[str] = ..., weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., typed_per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ..., host_rewrite_literal: _Optional[str] = ...) -> None: ...
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_KEY_PREFIX_FIELD_NUMBER: _ClassVar[int]
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    USE_HASH_POLICY_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedCompositeFieldContainer[WeightedCluster.ClusterWeight]
    total_weight: _wrappers_pb2.UInt32Value
    runtime_key_prefix: str
    header_name: str
    use_hash_policy: _wrappers_pb2.BoolValue
    def __init__(self, clusters: _Optional[_Iterable[_Union[WeightedCluster.ClusterWeight, _Mapping]]] = ..., total_weight: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., runtime_key_prefix: _Optional[str] = ..., header_name: _Optional[str] = ..., use_hash_policy: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class ClusterSpecifierPlugin(_message.Message):
    __slots__ = ("extension", "is_optional")
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    IS_OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    extension: _extension_pb2.TypedExtensionConfig
    is_optional: bool
    def __init__(self, extension: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., is_optional: bool = ...) -> None: ...

class RouteMatch(_message.Message):
    __slots__ = ("prefix", "path", "safe_regex", "connect_matcher", "path_separated_prefix", "path_match_policy", "case_sensitive", "runtime_fraction", "headers", "query_parameters", "grpc", "tls_context", "dynamic_metadata", "filter_state")
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
    class ConnectMatcher(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SAFE_REGEX_FIELD_NUMBER: _ClassVar[int]
    CONNECT_MATCHER_FIELD_NUMBER: _ClassVar[int]
    PATH_SEPARATED_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PATH_MATCH_POLICY_FIELD_NUMBER: _ClassVar[int]
    CASE_SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    GRPC_FIELD_NUMBER: _ClassVar[int]
    TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATE_FIELD_NUMBER: _ClassVar[int]
    prefix: str
    path: str
    safe_regex: _regex_pb2.RegexMatcher
    connect_matcher: RouteMatch.ConnectMatcher
    path_separated_prefix: str
    path_match_policy: _extension_pb2.TypedExtensionConfig
    case_sensitive: _wrappers_pb2.BoolValue
    runtime_fraction: _base_pb2.RuntimeFractionalPercent
    headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    query_parameters: _containers.RepeatedCompositeFieldContainer[QueryParameterMatcher]
    grpc: RouteMatch.GrpcRouteMatchOptions
    tls_context: RouteMatch.TlsContextMatchOptions
    dynamic_metadata: _containers.RepeatedCompositeFieldContainer[_metadata_pb2.MetadataMatcher]
    filter_state: _containers.RepeatedCompositeFieldContainer[_filter_state_pb2.FilterStateMatcher]
    def __init__(self, prefix: _Optional[str] = ..., path: _Optional[str] = ..., safe_regex: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., connect_matcher: _Optional[_Union[RouteMatch.ConnectMatcher, _Mapping]] = ..., path_separated_prefix: _Optional[str] = ..., path_match_policy: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., case_sensitive: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ..., query_parameters: _Optional[_Iterable[_Union[QueryParameterMatcher, _Mapping]]] = ..., grpc: _Optional[_Union[RouteMatch.GrpcRouteMatchOptions, _Mapping]] = ..., tls_context: _Optional[_Union[RouteMatch.TlsContextMatchOptions, _Mapping]] = ..., dynamic_metadata: _Optional[_Iterable[_Union[_metadata_pb2.MetadataMatcher, _Mapping]]] = ..., filter_state: _Optional[_Iterable[_Union[_filter_state_pb2.FilterStateMatcher, _Mapping]]] = ...) -> None: ...

class CorsPolicy(_message.Message):
    __slots__ = ("allow_origin_string_match", "allow_methods", "allow_headers", "expose_headers", "max_age", "allow_credentials", "filter_enabled", "shadow_enabled", "allow_private_network_access", "forward_not_matching_preflights")
    ALLOW_ORIGIN_STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    ALLOW_METHODS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_HEADERS_FIELD_NUMBER: _ClassVar[int]
    EXPOSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    MAX_AGE_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SHADOW_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PRIVATE_NETWORK_ACCESS_FIELD_NUMBER: _ClassVar[int]
    FORWARD_NOT_MATCHING_PREFLIGHTS_FIELD_NUMBER: _ClassVar[int]
    allow_origin_string_match: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    allow_methods: str
    allow_headers: str
    expose_headers: str
    max_age: str
    allow_credentials: _wrappers_pb2.BoolValue
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    shadow_enabled: _base_pb2.RuntimeFractionalPercent
    allow_private_network_access: _wrappers_pb2.BoolValue
    forward_not_matching_preflights: _wrappers_pb2.BoolValue
    def __init__(self, allow_origin_string_match: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., allow_methods: _Optional[str] = ..., allow_headers: _Optional[str] = ..., expose_headers: _Optional[str] = ..., max_age: _Optional[str] = ..., allow_credentials: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., shadow_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., allow_private_network_access: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., forward_not_matching_preflights: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class RouteAction(_message.Message):
    __slots__ = ("cluster", "cluster_header", "weighted_clusters", "cluster_specifier_plugin", "inline_cluster_specifier_plugin", "cluster_not_found_response_code", "metadata_match", "prefix_rewrite", "regex_rewrite", "path_rewrite_policy", "host_rewrite_literal", "auto_host_rewrite", "host_rewrite_header", "host_rewrite_path_regex", "append_x_forwarded_host", "timeout", "idle_timeout", "flush_timeout", "early_data_policy", "retry_policy", "retry_policy_typed_config", "request_mirror_policies", "priority", "rate_limits", "include_vh_rate_limits", "hash_policy", "cors", "max_grpc_timeout", "grpc_timeout_offset", "upgrade_configs", "internal_redirect_policy", "internal_redirect_action", "max_internal_redirects", "hedge_policy", "max_stream_duration")
    class ClusterNotFoundResponseCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SERVICE_UNAVAILABLE: _ClassVar[RouteAction.ClusterNotFoundResponseCode]
        NOT_FOUND: _ClassVar[RouteAction.ClusterNotFoundResponseCode]
        INTERNAL_SERVER_ERROR: _ClassVar[RouteAction.ClusterNotFoundResponseCode]
    SERVICE_UNAVAILABLE: RouteAction.ClusterNotFoundResponseCode
    NOT_FOUND: RouteAction.ClusterNotFoundResponseCode
    INTERNAL_SERVER_ERROR: RouteAction.ClusterNotFoundResponseCode
    class InternalRedirectAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PASS_THROUGH_INTERNAL_REDIRECT: _ClassVar[RouteAction.InternalRedirectAction]
        HANDLE_INTERNAL_REDIRECT: _ClassVar[RouteAction.InternalRedirectAction]
    PASS_THROUGH_INTERNAL_REDIRECT: RouteAction.InternalRedirectAction
    HANDLE_INTERNAL_REDIRECT: RouteAction.InternalRedirectAction
    class RequestMirrorPolicy(_message.Message):
        __slots__ = ("cluster", "cluster_header", "runtime_fraction", "trace_sampled", "disable_shadow_host_suffix_append", "request_headers_mutations", "host_rewrite_literal")
        CLUSTER_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_HEADER_FIELD_NUMBER: _ClassVar[int]
        RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
        TRACE_SAMPLED_FIELD_NUMBER: _ClassVar[int]
        DISABLE_SHADOW_HOST_SUFFIX_APPEND_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
        HOST_REWRITE_LITERAL_FIELD_NUMBER: _ClassVar[int]
        cluster: str
        cluster_header: str
        runtime_fraction: _base_pb2.RuntimeFractionalPercent
        trace_sampled: _wrappers_pb2.BoolValue
        disable_shadow_host_suffix_append: bool
        request_headers_mutations: _containers.RepeatedCompositeFieldContainer[_mutation_rules_pb2.HeaderMutation]
        host_rewrite_literal: str
        def __init__(self, cluster: _Optional[str] = ..., cluster_header: _Optional[str] = ..., runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., trace_sampled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., disable_shadow_host_suffix_append: bool = ..., request_headers_mutations: _Optional[_Iterable[_Union[_mutation_rules_pb2.HeaderMutation, _Mapping]]] = ..., host_rewrite_literal: _Optional[str] = ...) -> None: ...
    class HashPolicy(_message.Message):
        __slots__ = ("header", "cookie", "connection_properties", "query_parameter", "filter_state", "terminal")
        class Header(_message.Message):
            __slots__ = ("header_name", "regex_rewrite")
            HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
            REGEX_REWRITE_FIELD_NUMBER: _ClassVar[int]
            header_name: str
            regex_rewrite: _regex_pb2.RegexMatchAndSubstitute
            def __init__(self, header_name: _Optional[str] = ..., regex_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ...) -> None: ...
        class CookieAttribute(_message.Message):
            __slots__ = ("name", "value")
            NAME_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            name: str
            value: str
            def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        class Cookie(_message.Message):
            __slots__ = ("name", "ttl", "path", "attributes")
            NAME_FIELD_NUMBER: _ClassVar[int]
            TTL_FIELD_NUMBER: _ClassVar[int]
            PATH_FIELD_NUMBER: _ClassVar[int]
            ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
            name: str
            ttl: _duration_pb2.Duration
            path: str
            attributes: _containers.RepeatedCompositeFieldContainer[RouteAction.HashPolicy.CookieAttribute]
            def __init__(self, name: _Optional[str] = ..., ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., path: _Optional[str] = ..., attributes: _Optional[_Iterable[_Union[RouteAction.HashPolicy.CookieAttribute, _Mapping]]] = ...) -> None: ...
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
        __slots__ = ("upgrade_type", "enabled", "connect_config")
        class ConnectConfig(_message.Message):
            __slots__ = ("proxy_protocol_config", "allow_post")
            PROXY_PROTOCOL_CONFIG_FIELD_NUMBER: _ClassVar[int]
            ALLOW_POST_FIELD_NUMBER: _ClassVar[int]
            proxy_protocol_config: _proxy_protocol_pb2.ProxyProtocolConfig
            allow_post: bool
            def __init__(self, proxy_protocol_config: _Optional[_Union[_proxy_protocol_pb2.ProxyProtocolConfig, _Mapping]] = ..., allow_post: bool = ...) -> None: ...
        UPGRADE_TYPE_FIELD_NUMBER: _ClassVar[int]
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        CONNECT_CONFIG_FIELD_NUMBER: _ClassVar[int]
        upgrade_type: str
        enabled: _wrappers_pb2.BoolValue
        connect_config: RouteAction.UpgradeConfig.ConnectConfig
        def __init__(self, upgrade_type: _Optional[str] = ..., enabled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., connect_config: _Optional[_Union[RouteAction.UpgradeConfig.ConnectConfig, _Mapping]] = ...) -> None: ...
    class MaxStreamDuration(_message.Message):
        __slots__ = ("max_stream_duration", "grpc_timeout_header_max", "grpc_timeout_header_offset")
        MAX_STREAM_DURATION_FIELD_NUMBER: _ClassVar[int]
        GRPC_TIMEOUT_HEADER_MAX_FIELD_NUMBER: _ClassVar[int]
        GRPC_TIMEOUT_HEADER_OFFSET_FIELD_NUMBER: _ClassVar[int]
        max_stream_duration: _duration_pb2.Duration
        grpc_timeout_header_max: _duration_pb2.Duration
        grpc_timeout_header_offset: _duration_pb2.Duration
        def __init__(self, max_stream_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., grpc_timeout_header_max: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., grpc_timeout_header_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_HEADER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_SPECIFIER_PLUGIN_FIELD_NUMBER: _ClassVar[int]
    INLINE_CLUSTER_SPECIFIER_PLUGIN_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NOT_FOUND_RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    PREFIX_REWRITE_FIELD_NUMBER: _ClassVar[int]
    REGEX_REWRITE_FIELD_NUMBER: _ClassVar[int]
    PATH_REWRITE_POLICY_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_LITERAL_FIELD_NUMBER: _ClassVar[int]
    AUTO_HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_HEADER_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_PATH_REGEX_FIELD_NUMBER: _ClassVar[int]
    APPEND_X_FORWARDED_HOST_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FLUSH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    EARLY_DATA_POLICY_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MIRROR_POLICIES_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_VH_RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    HASH_POLICY_FIELD_NUMBER: _ClassVar[int]
    CORS_FIELD_NUMBER: _ClassVar[int]
    MAX_GRPC_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    GRPC_TIMEOUT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    UPGRADE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REDIRECT_POLICY_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REDIRECT_ACTION_FIELD_NUMBER: _ClassVar[int]
    MAX_INTERNAL_REDIRECTS_FIELD_NUMBER: _ClassVar[int]
    HEDGE_POLICY_FIELD_NUMBER: _ClassVar[int]
    MAX_STREAM_DURATION_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    cluster_header: str
    weighted_clusters: WeightedCluster
    cluster_specifier_plugin: str
    inline_cluster_specifier_plugin: ClusterSpecifierPlugin
    cluster_not_found_response_code: RouteAction.ClusterNotFoundResponseCode
    metadata_match: _base_pb2.Metadata
    prefix_rewrite: str
    regex_rewrite: _regex_pb2.RegexMatchAndSubstitute
    path_rewrite_policy: _extension_pb2.TypedExtensionConfig
    host_rewrite_literal: str
    auto_host_rewrite: _wrappers_pb2.BoolValue
    host_rewrite_header: str
    host_rewrite_path_regex: _regex_pb2.RegexMatchAndSubstitute
    append_x_forwarded_host: bool
    timeout: _duration_pb2.Duration
    idle_timeout: _duration_pb2.Duration
    flush_timeout: _duration_pb2.Duration
    early_data_policy: _extension_pb2.TypedExtensionConfig
    retry_policy: RetryPolicy
    retry_policy_typed_config: _any_pb2.Any
    request_mirror_policies: _containers.RepeatedCompositeFieldContainer[RouteAction.RequestMirrorPolicy]
    priority: _base_pb2.RoutingPriority
    rate_limits: _containers.RepeatedCompositeFieldContainer[RateLimit]
    include_vh_rate_limits: _wrappers_pb2.BoolValue
    hash_policy: _containers.RepeatedCompositeFieldContainer[RouteAction.HashPolicy]
    cors: CorsPolicy
    max_grpc_timeout: _duration_pb2.Duration
    grpc_timeout_offset: _duration_pb2.Duration
    upgrade_configs: _containers.RepeatedCompositeFieldContainer[RouteAction.UpgradeConfig]
    internal_redirect_policy: InternalRedirectPolicy
    internal_redirect_action: RouteAction.InternalRedirectAction
    max_internal_redirects: _wrappers_pb2.UInt32Value
    hedge_policy: HedgePolicy
    max_stream_duration: RouteAction.MaxStreamDuration
    def __init__(self, cluster: _Optional[str] = ..., cluster_header: _Optional[str] = ..., weighted_clusters: _Optional[_Union[WeightedCluster, _Mapping]] = ..., cluster_specifier_plugin: _Optional[str] = ..., inline_cluster_specifier_plugin: _Optional[_Union[ClusterSpecifierPlugin, _Mapping]] = ..., cluster_not_found_response_code: _Optional[_Union[RouteAction.ClusterNotFoundResponseCode, str]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., prefix_rewrite: _Optional[str] = ..., regex_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., path_rewrite_policy: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., host_rewrite_literal: _Optional[str] = ..., auto_host_rewrite: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., host_rewrite_header: _Optional[str] = ..., host_rewrite_path_regex: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., append_x_forwarded_host: bool = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., flush_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., early_data_policy: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., retry_policy: _Optional[_Union[RetryPolicy, _Mapping]] = ..., retry_policy_typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., request_mirror_policies: _Optional[_Iterable[_Union[RouteAction.RequestMirrorPolicy, _Mapping]]] = ..., priority: _Optional[_Union[_base_pb2.RoutingPriority, str]] = ..., rate_limits: _Optional[_Iterable[_Union[RateLimit, _Mapping]]] = ..., include_vh_rate_limits: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., hash_policy: _Optional[_Iterable[_Union[RouteAction.HashPolicy, _Mapping]]] = ..., cors: _Optional[_Union[CorsPolicy, _Mapping]] = ..., max_grpc_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., grpc_timeout_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upgrade_configs: _Optional[_Iterable[_Union[RouteAction.UpgradeConfig, _Mapping]]] = ..., internal_redirect_policy: _Optional[_Union[InternalRedirectPolicy, _Mapping]] = ..., internal_redirect_action: _Optional[_Union[RouteAction.InternalRedirectAction, str]] = ..., max_internal_redirects: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., hedge_policy: _Optional[_Union[HedgePolicy, _Mapping]] = ..., max_stream_duration: _Optional[_Union[RouteAction.MaxStreamDuration, _Mapping]] = ...) -> None: ...

class RetryPolicy(_message.Message):
    __slots__ = ("retry_on", "num_retries", "per_try_timeout", "per_try_idle_timeout", "retry_priority", "retry_host_predicate", "retry_options_predicates", "host_selection_retry_max_attempts", "retriable_status_codes", "retry_back_off", "rate_limited_retry_back_off", "retriable_headers", "retriable_request_headers")
    class ResetHeaderFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SECONDS: _ClassVar[RetryPolicy.ResetHeaderFormat]
        UNIX_TIMESTAMP: _ClassVar[RetryPolicy.ResetHeaderFormat]
    SECONDS: RetryPolicy.ResetHeaderFormat
    UNIX_TIMESTAMP: RetryPolicy.ResetHeaderFormat
    class RetryPriority(_message.Message):
        __slots__ = ("name", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class RetryHostPredicate(_message.Message):
        __slots__ = ("name", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class RetryBackOff(_message.Message):
        __slots__ = ("base_interval", "max_interval")
        BASE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        MAX_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        base_interval: _duration_pb2.Duration
        max_interval: _duration_pb2.Duration
        def __init__(self, base_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class ResetHeader(_message.Message):
        __slots__ = ("name", "format")
        NAME_FIELD_NUMBER: _ClassVar[int]
        FORMAT_FIELD_NUMBER: _ClassVar[int]
        name: str
        format: RetryPolicy.ResetHeaderFormat
        def __init__(self, name: _Optional[str] = ..., format: _Optional[_Union[RetryPolicy.ResetHeaderFormat, str]] = ...) -> None: ...
    class RateLimitedRetryBackOff(_message.Message):
        __slots__ = ("reset_headers", "max_interval")
        RESET_HEADERS_FIELD_NUMBER: _ClassVar[int]
        MAX_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        reset_headers: _containers.RepeatedCompositeFieldContainer[RetryPolicy.ResetHeader]
        max_interval: _duration_pb2.Duration
        def __init__(self, reset_headers: _Optional[_Iterable[_Union[RetryPolicy.ResetHeader, _Mapping]]] = ..., max_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    RETRY_ON_FIELD_NUMBER: _ClassVar[int]
    NUM_RETRIES_FIELD_NUMBER: _ClassVar[int]
    PER_TRY_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    PER_TRY_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    RETRY_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    RETRY_HOST_PREDICATE_FIELD_NUMBER: _ClassVar[int]
    RETRY_OPTIONS_PREDICATES_FIELD_NUMBER: _ClassVar[int]
    HOST_SELECTION_RETRY_MAX_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    RETRIABLE_STATUS_CODES_FIELD_NUMBER: _ClassVar[int]
    RETRY_BACK_OFF_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITED_RETRY_BACK_OFF_FIELD_NUMBER: _ClassVar[int]
    RETRIABLE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RETRIABLE_REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    retry_on: str
    num_retries: _wrappers_pb2.UInt32Value
    per_try_timeout: _duration_pb2.Duration
    per_try_idle_timeout: _duration_pb2.Duration
    retry_priority: RetryPolicy.RetryPriority
    retry_host_predicate: _containers.RepeatedCompositeFieldContainer[RetryPolicy.RetryHostPredicate]
    retry_options_predicates: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    host_selection_retry_max_attempts: int
    retriable_status_codes: _containers.RepeatedScalarFieldContainer[int]
    retry_back_off: RetryPolicy.RetryBackOff
    rate_limited_retry_back_off: RetryPolicy.RateLimitedRetryBackOff
    retriable_headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    retriable_request_headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    def __init__(self, retry_on: _Optional[str] = ..., num_retries: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., per_try_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., per_try_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., retry_priority: _Optional[_Union[RetryPolicy.RetryPriority, _Mapping]] = ..., retry_host_predicate: _Optional[_Iterable[_Union[RetryPolicy.RetryHostPredicate, _Mapping]]] = ..., retry_options_predicates: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., host_selection_retry_max_attempts: _Optional[int] = ..., retriable_status_codes: _Optional[_Iterable[int]] = ..., retry_back_off: _Optional[_Union[RetryPolicy.RetryBackOff, _Mapping]] = ..., rate_limited_retry_back_off: _Optional[_Union[RetryPolicy.RateLimitedRetryBackOff, _Mapping]] = ..., retriable_headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ..., retriable_request_headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("https_redirect", "scheme_redirect", "host_redirect", "port_redirect", "path_redirect", "prefix_rewrite", "regex_rewrite", "response_code", "strip_query")
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
    REGEX_REWRITE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    STRIP_QUERY_FIELD_NUMBER: _ClassVar[int]
    https_redirect: bool
    scheme_redirect: str
    host_redirect: str
    port_redirect: int
    path_redirect: str
    prefix_rewrite: str
    regex_rewrite: _regex_pb2.RegexMatchAndSubstitute
    response_code: RedirectAction.RedirectResponseCode
    strip_query: bool
    def __init__(self, https_redirect: bool = ..., scheme_redirect: _Optional[str] = ..., host_redirect: _Optional[str] = ..., port_redirect: _Optional[int] = ..., path_redirect: _Optional[str] = ..., prefix_rewrite: _Optional[str] = ..., regex_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., response_code: _Optional[_Union[RedirectAction.RedirectResponseCode, str]] = ..., strip_query: bool = ...) -> None: ...

class DirectResponseAction(_message.Message):
    __slots__ = ("status", "body")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    status: int
    body: _base_pb2.DataSource
    def __init__(self, status: _Optional[int] = ..., body: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...

class NonForwardingAction(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

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
    __slots__ = ("headers", "name")
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
    name: str
    def __init__(self, headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ..., name: _Optional[str] = ...) -> None: ...

class RateLimit(_message.Message):
    __slots__ = ("stage", "disable_key", "actions", "limit", "hits_addend", "apply_on_stream_done")
    class Action(_message.Message):
        __slots__ = ("source_cluster", "destination_cluster", "request_headers", "query_parameters", "remote_address", "generic_key", "header_value_match", "dynamic_metadata", "metadata", "extension", "masked_remote_address", "query_parameter_value_match")
        class SourceCluster(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class DestinationCluster(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class RequestHeaders(_message.Message):
            __slots__ = ("header_name", "descriptor_key", "skip_if_absent")
            HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            SKIP_IF_ABSENT_FIELD_NUMBER: _ClassVar[int]
            header_name: str
            descriptor_key: str
            skip_if_absent: bool
            def __init__(self, header_name: _Optional[str] = ..., descriptor_key: _Optional[str] = ..., skip_if_absent: bool = ...) -> None: ...
        class QueryParameters(_message.Message):
            __slots__ = ("query_parameter_name", "descriptor_key", "skip_if_absent")
            QUERY_PARAMETER_NAME_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            SKIP_IF_ABSENT_FIELD_NUMBER: _ClassVar[int]
            query_parameter_name: str
            descriptor_key: str
            skip_if_absent: bool
            def __init__(self, query_parameter_name: _Optional[str] = ..., descriptor_key: _Optional[str] = ..., skip_if_absent: bool = ...) -> None: ...
        class RemoteAddress(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class MaskedRemoteAddress(_message.Message):
            __slots__ = ("v4_prefix_mask_len", "v6_prefix_mask_len")
            V4_PREFIX_MASK_LEN_FIELD_NUMBER: _ClassVar[int]
            V6_PREFIX_MASK_LEN_FIELD_NUMBER: _ClassVar[int]
            v4_prefix_mask_len: _wrappers_pb2.UInt32Value
            v6_prefix_mask_len: _wrappers_pb2.UInt32Value
            def __init__(self, v4_prefix_mask_len: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., v6_prefix_mask_len: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
        class GenericKey(_message.Message):
            __slots__ = ("descriptor_value", "descriptor_key")
            DESCRIPTOR_VALUE_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            descriptor_value: str
            descriptor_key: str
            def __init__(self, descriptor_value: _Optional[str] = ..., descriptor_key: _Optional[str] = ...) -> None: ...
        class HeaderValueMatch(_message.Message):
            __slots__ = ("descriptor_key", "descriptor_value", "expect_match", "headers")
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTOR_VALUE_FIELD_NUMBER: _ClassVar[int]
            EXPECT_MATCH_FIELD_NUMBER: _ClassVar[int]
            HEADERS_FIELD_NUMBER: _ClassVar[int]
            descriptor_key: str
            descriptor_value: str
            expect_match: _wrappers_pb2.BoolValue
            headers: _containers.RepeatedCompositeFieldContainer[HeaderMatcher]
            def __init__(self, descriptor_key: _Optional[str] = ..., descriptor_value: _Optional[str] = ..., expect_match: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., headers: _Optional[_Iterable[_Union[HeaderMatcher, _Mapping]]] = ...) -> None: ...
        class DynamicMetaData(_message.Message):
            __slots__ = ("descriptor_key", "metadata_key", "default_value")
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            METADATA_KEY_FIELD_NUMBER: _ClassVar[int]
            DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
            descriptor_key: str
            metadata_key: _metadata_pb2_1.MetadataKey
            default_value: str
            def __init__(self, descriptor_key: _Optional[str] = ..., metadata_key: _Optional[_Union[_metadata_pb2_1.MetadataKey, _Mapping]] = ..., default_value: _Optional[str] = ...) -> None: ...
        class MetaData(_message.Message):
            __slots__ = ("descriptor_key", "metadata_key", "default_value", "source", "skip_if_absent")
            class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
                __slots__ = ()
                DYNAMIC: _ClassVar[RateLimit.Action.MetaData.Source]
                ROUTE_ENTRY: _ClassVar[RateLimit.Action.MetaData.Source]
            DYNAMIC: RateLimit.Action.MetaData.Source
            ROUTE_ENTRY: RateLimit.Action.MetaData.Source
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            METADATA_KEY_FIELD_NUMBER: _ClassVar[int]
            DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
            SOURCE_FIELD_NUMBER: _ClassVar[int]
            SKIP_IF_ABSENT_FIELD_NUMBER: _ClassVar[int]
            descriptor_key: str
            metadata_key: _metadata_pb2_1.MetadataKey
            default_value: str
            source: RateLimit.Action.MetaData.Source
            skip_if_absent: bool
            def __init__(self, descriptor_key: _Optional[str] = ..., metadata_key: _Optional[_Union[_metadata_pb2_1.MetadataKey, _Mapping]] = ..., default_value: _Optional[str] = ..., source: _Optional[_Union[RateLimit.Action.MetaData.Source, str]] = ..., skip_if_absent: bool = ...) -> None: ...
        class QueryParameterValueMatch(_message.Message):
            __slots__ = ("descriptor_key", "descriptor_value", "expect_match", "query_parameters")
            DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTOR_VALUE_FIELD_NUMBER: _ClassVar[int]
            EXPECT_MATCH_FIELD_NUMBER: _ClassVar[int]
            QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
            descriptor_key: str
            descriptor_value: str
            expect_match: _wrappers_pb2.BoolValue
            query_parameters: _containers.RepeatedCompositeFieldContainer[QueryParameterMatcher]
            def __init__(self, descriptor_key: _Optional[str] = ..., descriptor_value: _Optional[str] = ..., expect_match: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., query_parameters: _Optional[_Iterable[_Union[QueryParameterMatcher, _Mapping]]] = ...) -> None: ...
        SOURCE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
        DESTINATION_CLUSTER_FIELD_NUMBER: _ClassVar[int]
        REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
        QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
        REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        GENERIC_KEY_FIELD_NUMBER: _ClassVar[int]
        HEADER_VALUE_MATCH_FIELD_NUMBER: _ClassVar[int]
        DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        EXTENSION_FIELD_NUMBER: _ClassVar[int]
        MASKED_REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        QUERY_PARAMETER_VALUE_MATCH_FIELD_NUMBER: _ClassVar[int]
        source_cluster: RateLimit.Action.SourceCluster
        destination_cluster: RateLimit.Action.DestinationCluster
        request_headers: RateLimit.Action.RequestHeaders
        query_parameters: RateLimit.Action.QueryParameters
        remote_address: RateLimit.Action.RemoteAddress
        generic_key: RateLimit.Action.GenericKey
        header_value_match: RateLimit.Action.HeaderValueMatch
        dynamic_metadata: RateLimit.Action.DynamicMetaData
        metadata: RateLimit.Action.MetaData
        extension: _extension_pb2.TypedExtensionConfig
        masked_remote_address: RateLimit.Action.MaskedRemoteAddress
        query_parameter_value_match: RateLimit.Action.QueryParameterValueMatch
        def __init__(self, source_cluster: _Optional[_Union[RateLimit.Action.SourceCluster, _Mapping]] = ..., destination_cluster: _Optional[_Union[RateLimit.Action.DestinationCluster, _Mapping]] = ..., request_headers: _Optional[_Union[RateLimit.Action.RequestHeaders, _Mapping]] = ..., query_parameters: _Optional[_Union[RateLimit.Action.QueryParameters, _Mapping]] = ..., remote_address: _Optional[_Union[RateLimit.Action.RemoteAddress, _Mapping]] = ..., generic_key: _Optional[_Union[RateLimit.Action.GenericKey, _Mapping]] = ..., header_value_match: _Optional[_Union[RateLimit.Action.HeaderValueMatch, _Mapping]] = ..., dynamic_metadata: _Optional[_Union[RateLimit.Action.DynamicMetaData, _Mapping]] = ..., metadata: _Optional[_Union[RateLimit.Action.MetaData, _Mapping]] = ..., extension: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., masked_remote_address: _Optional[_Union[RateLimit.Action.MaskedRemoteAddress, _Mapping]] = ..., query_parameter_value_match: _Optional[_Union[RateLimit.Action.QueryParameterValueMatch, _Mapping]] = ...) -> None: ...
    class Override(_message.Message):
        __slots__ = ("dynamic_metadata",)
        class DynamicMetadata(_message.Message):
            __slots__ = ("metadata_key",)
            METADATA_KEY_FIELD_NUMBER: _ClassVar[int]
            metadata_key: _metadata_pb2_1.MetadataKey
            def __init__(self, metadata_key: _Optional[_Union[_metadata_pb2_1.MetadataKey, _Mapping]] = ...) -> None: ...
        DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
        dynamic_metadata: RateLimit.Override.DynamicMetadata
        def __init__(self, dynamic_metadata: _Optional[_Union[RateLimit.Override.DynamicMetadata, _Mapping]] = ...) -> None: ...
    class HitsAddend(_message.Message):
        __slots__ = ("number", "format")
        NUMBER_FIELD_NUMBER: _ClassVar[int]
        FORMAT_FIELD_NUMBER: _ClassVar[int]
        number: _wrappers_pb2.UInt64Value
        format: str
        def __init__(self, number: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., format: _Optional[str] = ...) -> None: ...
    STAGE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_KEY_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    HITS_ADDEND_FIELD_NUMBER: _ClassVar[int]
    APPLY_ON_STREAM_DONE_FIELD_NUMBER: _ClassVar[int]
    stage: _wrappers_pb2.UInt32Value
    disable_key: str
    actions: _containers.RepeatedCompositeFieldContainer[RateLimit.Action]
    limit: RateLimit.Override
    hits_addend: RateLimit.HitsAddend
    apply_on_stream_done: bool
    def __init__(self, stage: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., disable_key: _Optional[str] = ..., actions: _Optional[_Iterable[_Union[RateLimit.Action, _Mapping]]] = ..., limit: _Optional[_Union[RateLimit.Override, _Mapping]] = ..., hits_addend: _Optional[_Union[RateLimit.HitsAddend, _Mapping]] = ..., apply_on_stream_done: bool = ...) -> None: ...

class HeaderMatcher(_message.Message):
    __slots__ = ("name", "exact_match", "safe_regex_match", "range_match", "present_match", "prefix_match", "suffix_match", "contains_match", "string_match", "invert_match", "treat_missing_header_as_empty")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXACT_MATCH_FIELD_NUMBER: _ClassVar[int]
    SAFE_REGEX_MATCH_FIELD_NUMBER: _ClassVar[int]
    RANGE_MATCH_FIELD_NUMBER: _ClassVar[int]
    PRESENT_MATCH_FIELD_NUMBER: _ClassVar[int]
    PREFIX_MATCH_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_MATCH_FIELD_NUMBER: _ClassVar[int]
    CONTAINS_MATCH_FIELD_NUMBER: _ClassVar[int]
    STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    INVERT_MATCH_FIELD_NUMBER: _ClassVar[int]
    TREAT_MISSING_HEADER_AS_EMPTY_FIELD_NUMBER: _ClassVar[int]
    name: str
    exact_match: str
    safe_regex_match: _regex_pb2.RegexMatcher
    range_match: _range_pb2.Int64Range
    present_match: bool
    prefix_match: str
    suffix_match: str
    contains_match: str
    string_match: _string_pb2.StringMatcher
    invert_match: bool
    treat_missing_header_as_empty: bool
    def __init__(self, name: _Optional[str] = ..., exact_match: _Optional[str] = ..., safe_regex_match: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., range_match: _Optional[_Union[_range_pb2.Int64Range, _Mapping]] = ..., present_match: bool = ..., prefix_match: _Optional[str] = ..., suffix_match: _Optional[str] = ..., contains_match: _Optional[str] = ..., string_match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., invert_match: bool = ..., treat_missing_header_as_empty: bool = ...) -> None: ...

class QueryParameterMatcher(_message.Message):
    __slots__ = ("name", "string_match", "present_match")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    PRESENT_MATCH_FIELD_NUMBER: _ClassVar[int]
    name: str
    string_match: _string_pb2.StringMatcher
    present_match: bool
    def __init__(self, name: _Optional[str] = ..., string_match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., present_match: bool = ...) -> None: ...

class InternalRedirectPolicy(_message.Message):
    __slots__ = ("max_internal_redirects", "redirect_response_codes", "predicates", "allow_cross_scheme_redirect", "response_headers_to_copy")
    MAX_INTERNAL_REDIRECTS_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_RESPONSE_CODES_FIELD_NUMBER: _ClassVar[int]
    PREDICATES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CROSS_SCHEME_REDIRECT_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_COPY_FIELD_NUMBER: _ClassVar[int]
    max_internal_redirects: _wrappers_pb2.UInt32Value
    redirect_response_codes: _containers.RepeatedScalarFieldContainer[int]
    predicates: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    allow_cross_scheme_redirect: bool
    response_headers_to_copy: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, max_internal_redirects: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., redirect_response_codes: _Optional[_Iterable[int]] = ..., predicates: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., allow_cross_scheme_redirect: bool = ..., response_headers_to_copy: _Optional[_Iterable[str]] = ...) -> None: ...

class FilterConfig(_message.Message):
    __slots__ = ("config", "is_optional", "disabled")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    IS_OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    config: _any_pb2.Any
    is_optional: bool
    disabled: bool
    def __init__(self, config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., is_optional: bool = ..., disabled: bool = ...) -> None: ...
