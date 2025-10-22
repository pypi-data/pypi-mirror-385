import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import http_uri_pb2 as _http_uri_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JwtProvider(_message.Message):
    __slots__ = ("issuer", "audiences", "subjects", "require_expiration", "max_lifetime", "remote_jwks", "local_jwks", "forward", "from_headers", "from_params", "from_cookies", "forward_payload_header", "pad_forward_payload_header", "payload_in_metadata", "normalize_payload_in_metadata", "header_in_metadata", "failed_status_in_metadata", "clock_skew_seconds", "jwt_cache_config", "claim_to_headers", "clear_route_cache")
    class NormalizePayload(_message.Message):
        __slots__ = ("space_delimited_claims",)
        SPACE_DELIMITED_CLAIMS_FIELD_NUMBER: _ClassVar[int]
        space_delimited_claims: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, space_delimited_claims: _Optional[_Iterable[str]] = ...) -> None: ...
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    AUDIENCES_FIELD_NUMBER: _ClassVar[int]
    SUBJECTS_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    MAX_LIFETIME_FIELD_NUMBER: _ClassVar[int]
    REMOTE_JWKS_FIELD_NUMBER: _ClassVar[int]
    LOCAL_JWKS_FIELD_NUMBER: _ClassVar[int]
    FORWARD_FIELD_NUMBER: _ClassVar[int]
    FROM_HEADERS_FIELD_NUMBER: _ClassVar[int]
    FROM_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FROM_COOKIES_FIELD_NUMBER: _ClassVar[int]
    FORWARD_PAYLOAD_HEADER_FIELD_NUMBER: _ClassVar[int]
    PAD_FORWARD_PAYLOAD_HEADER_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_IN_METADATA_FIELD_NUMBER: _ClassVar[int]
    NORMALIZE_PAYLOAD_IN_METADATA_FIELD_NUMBER: _ClassVar[int]
    HEADER_IN_METADATA_FIELD_NUMBER: _ClassVar[int]
    FAILED_STATUS_IN_METADATA_FIELD_NUMBER: _ClassVar[int]
    CLOCK_SKEW_SECONDS_FIELD_NUMBER: _ClassVar[int]
    JWT_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CLAIM_TO_HEADERS_FIELD_NUMBER: _ClassVar[int]
    CLEAR_ROUTE_CACHE_FIELD_NUMBER: _ClassVar[int]
    issuer: str
    audiences: _containers.RepeatedScalarFieldContainer[str]
    subjects: _string_pb2.StringMatcher
    require_expiration: bool
    max_lifetime: _duration_pb2.Duration
    remote_jwks: RemoteJwks
    local_jwks: _base_pb2.DataSource
    forward: bool
    from_headers: _containers.RepeatedCompositeFieldContainer[JwtHeader]
    from_params: _containers.RepeatedScalarFieldContainer[str]
    from_cookies: _containers.RepeatedScalarFieldContainer[str]
    forward_payload_header: str
    pad_forward_payload_header: bool
    payload_in_metadata: str
    normalize_payload_in_metadata: JwtProvider.NormalizePayload
    header_in_metadata: str
    failed_status_in_metadata: str
    clock_skew_seconds: int
    jwt_cache_config: JwtCacheConfig
    claim_to_headers: _containers.RepeatedCompositeFieldContainer[JwtClaimToHeader]
    clear_route_cache: bool
    def __init__(self, issuer: _Optional[str] = ..., audiences: _Optional[_Iterable[str]] = ..., subjects: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., require_expiration: bool = ..., max_lifetime: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., remote_jwks: _Optional[_Union[RemoteJwks, _Mapping]] = ..., local_jwks: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., forward: bool = ..., from_headers: _Optional[_Iterable[_Union[JwtHeader, _Mapping]]] = ..., from_params: _Optional[_Iterable[str]] = ..., from_cookies: _Optional[_Iterable[str]] = ..., forward_payload_header: _Optional[str] = ..., pad_forward_payload_header: bool = ..., payload_in_metadata: _Optional[str] = ..., normalize_payload_in_metadata: _Optional[_Union[JwtProvider.NormalizePayload, _Mapping]] = ..., header_in_metadata: _Optional[str] = ..., failed_status_in_metadata: _Optional[str] = ..., clock_skew_seconds: _Optional[int] = ..., jwt_cache_config: _Optional[_Union[JwtCacheConfig, _Mapping]] = ..., claim_to_headers: _Optional[_Iterable[_Union[JwtClaimToHeader, _Mapping]]] = ..., clear_route_cache: bool = ...) -> None: ...

class JwtCacheConfig(_message.Message):
    __slots__ = ("jwt_cache_size", "jwt_max_token_size")
    JWT_CACHE_SIZE_FIELD_NUMBER: _ClassVar[int]
    JWT_MAX_TOKEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    jwt_cache_size: int
    jwt_max_token_size: int
    def __init__(self, jwt_cache_size: _Optional[int] = ..., jwt_max_token_size: _Optional[int] = ...) -> None: ...

class RemoteJwks(_message.Message):
    __slots__ = ("http_uri", "cache_duration", "async_fetch", "retry_policy")
    HTTP_URI_FIELD_NUMBER: _ClassVar[int]
    CACHE_DURATION_FIELD_NUMBER: _ClassVar[int]
    ASYNC_FETCH_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    http_uri: _http_uri_pb2.HttpUri
    cache_duration: _duration_pb2.Duration
    async_fetch: JwksAsyncFetch
    retry_policy: _base_pb2.RetryPolicy
    def __init__(self, http_uri: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., cache_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., async_fetch: _Optional[_Union[JwksAsyncFetch, _Mapping]] = ..., retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ...) -> None: ...

class JwksAsyncFetch(_message.Message):
    __slots__ = ("fast_listener", "failed_refetch_duration")
    FAST_LISTENER_FIELD_NUMBER: _ClassVar[int]
    FAILED_REFETCH_DURATION_FIELD_NUMBER: _ClassVar[int]
    fast_listener: bool
    failed_refetch_duration: _duration_pb2.Duration
    def __init__(self, fast_listener: bool = ..., failed_refetch_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class JwtHeader(_message.Message):
    __slots__ = ("name", "value_prefix")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    name: str
    value_prefix: str
    def __init__(self, name: _Optional[str] = ..., value_prefix: _Optional[str] = ...) -> None: ...

class ProviderWithAudiences(_message.Message):
    __slots__ = ("provider_name", "audiences")
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    AUDIENCES_FIELD_NUMBER: _ClassVar[int]
    provider_name: str
    audiences: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, provider_name: _Optional[str] = ..., audiences: _Optional[_Iterable[str]] = ...) -> None: ...

class JwtRequirement(_message.Message):
    __slots__ = ("provider_name", "provider_and_audiences", "requires_any", "requires_all", "allow_missing_or_failed", "allow_missing")
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_AND_AUDIENCES_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_ANY_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_ALL_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_OR_FAILED_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_FIELD_NUMBER: _ClassVar[int]
    provider_name: str
    provider_and_audiences: ProviderWithAudiences
    requires_any: JwtRequirementOrList
    requires_all: JwtRequirementAndList
    allow_missing_or_failed: _empty_pb2.Empty
    allow_missing: _empty_pb2.Empty
    def __init__(self, provider_name: _Optional[str] = ..., provider_and_audiences: _Optional[_Union[ProviderWithAudiences, _Mapping]] = ..., requires_any: _Optional[_Union[JwtRequirementOrList, _Mapping]] = ..., requires_all: _Optional[_Union[JwtRequirementAndList, _Mapping]] = ..., allow_missing_or_failed: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., allow_missing: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class JwtRequirementOrList(_message.Message):
    __slots__ = ("requirements",)
    REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    requirements: _containers.RepeatedCompositeFieldContainer[JwtRequirement]
    def __init__(self, requirements: _Optional[_Iterable[_Union[JwtRequirement, _Mapping]]] = ...) -> None: ...

class JwtRequirementAndList(_message.Message):
    __slots__ = ("requirements",)
    REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    requirements: _containers.RepeatedCompositeFieldContainer[JwtRequirement]
    def __init__(self, requirements: _Optional[_Iterable[_Union[JwtRequirement, _Mapping]]] = ...) -> None: ...

class RequirementRule(_message.Message):
    __slots__ = ("match", "requires", "requirement_name")
    MATCH_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    match: _route_components_pb2.RouteMatch
    requires: JwtRequirement
    requirement_name: str
    def __init__(self, match: _Optional[_Union[_route_components_pb2.RouteMatch, _Mapping]] = ..., requires: _Optional[_Union[JwtRequirement, _Mapping]] = ..., requirement_name: _Optional[str] = ...) -> None: ...

class FilterStateRule(_message.Message):
    __slots__ = ("name", "requires")
    class RequiresEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: JwtRequirement
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[JwtRequirement, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_FIELD_NUMBER: _ClassVar[int]
    name: str
    requires: _containers.MessageMap[str, JwtRequirement]
    def __init__(self, name: _Optional[str] = ..., requires: _Optional[_Mapping[str, JwtRequirement]] = ...) -> None: ...

class JwtAuthentication(_message.Message):
    __slots__ = ("providers", "rules", "filter_state_rules", "bypass_cors_preflight", "requirement_map", "strip_failure_response", "stat_prefix")
    class ProvidersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: JwtProvider
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[JwtProvider, _Mapping]] = ...) -> None: ...
    class RequirementMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: JwtRequirement
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[JwtRequirement, _Mapping]] = ...) -> None: ...
    PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATE_RULES_FIELD_NUMBER: _ClassVar[int]
    BYPASS_CORS_PREFLIGHT_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENT_MAP_FIELD_NUMBER: _ClassVar[int]
    STRIP_FAILURE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    providers: _containers.MessageMap[str, JwtProvider]
    rules: _containers.RepeatedCompositeFieldContainer[RequirementRule]
    filter_state_rules: FilterStateRule
    bypass_cors_preflight: bool
    requirement_map: _containers.MessageMap[str, JwtRequirement]
    strip_failure_response: bool
    stat_prefix: str
    def __init__(self, providers: _Optional[_Mapping[str, JwtProvider]] = ..., rules: _Optional[_Iterable[_Union[RequirementRule, _Mapping]]] = ..., filter_state_rules: _Optional[_Union[FilterStateRule, _Mapping]] = ..., bypass_cors_preflight: bool = ..., requirement_map: _Optional[_Mapping[str, JwtRequirement]] = ..., strip_failure_response: bool = ..., stat_prefix: _Optional[str] = ...) -> None: ...

class PerRouteConfig(_message.Message):
    __slots__ = ("disabled", "requirement_name")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    requirement_name: str
    def __init__(self, disabled: bool = ..., requirement_name: _Optional[str] = ...) -> None: ...

class JwtClaimToHeader(_message.Message):
    __slots__ = ("header_name", "claim_name")
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    CLAIM_NAME_FIELD_NUMBER: _ClassVar[int]
    header_name: str
    claim_name: str
    def __init__(self, header_name: _Optional[str] = ..., claim_name: _Optional[str] = ...) -> None: ...
