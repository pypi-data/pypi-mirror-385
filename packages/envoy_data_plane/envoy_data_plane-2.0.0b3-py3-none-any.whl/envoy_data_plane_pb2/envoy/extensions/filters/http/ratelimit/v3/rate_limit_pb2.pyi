import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.ratelimit.v3 import rls_pb2 as _rls_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from google.protobuf import duration_pb2 as _duration_pb2
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

class RateLimit(_message.Message):
    __slots__ = ("domain", "stage", "request_type", "timeout", "failure_mode_deny", "rate_limited_as_resource_exhausted", "rate_limit_service", "enable_x_ratelimit_headers", "disable_x_envoy_ratelimited_header", "rate_limited_status", "response_headers_to_add", "status_on_error", "stat_prefix", "filter_enabled", "filter_enforced", "failure_mode_deny_percent", "rate_limits")
    class XRateLimitHeadersRFCVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OFF: _ClassVar[RateLimit.XRateLimitHeadersRFCVersion]
        DRAFT_VERSION_03: _ClassVar[RateLimit.XRateLimitHeadersRFCVersion]
    OFF: RateLimit.XRateLimitHeadersRFCVersion
    DRAFT_VERSION_03: RateLimit.XRateLimitHeadersRFCVersion
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_DENY_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITED_AS_RESOURCE_EXHAUSTED_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMIT_SERVICE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_X_RATELIMIT_HEADERS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_X_ENVOY_RATELIMITED_HEADER_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITED_STATUS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    STATUS_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENFORCED_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_DENY_PERCENT_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    domain: str
    stage: int
    request_type: str
    timeout: _duration_pb2.Duration
    failure_mode_deny: bool
    rate_limited_as_resource_exhausted: bool
    rate_limit_service: _rls_pb2.RateLimitServiceConfig
    enable_x_ratelimit_headers: RateLimit.XRateLimitHeadersRFCVersion
    disable_x_envoy_ratelimited_header: bool
    rate_limited_status: _http_status_pb2.HttpStatus
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    status_on_error: _http_status_pb2.HttpStatus
    stat_prefix: str
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    filter_enforced: _base_pb2.RuntimeFractionalPercent
    failure_mode_deny_percent: _base_pb2.RuntimeFractionalPercent
    rate_limits: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.RateLimit]
    def __init__(self, domain: _Optional[str] = ..., stage: _Optional[int] = ..., request_type: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., failure_mode_deny: bool = ..., rate_limited_as_resource_exhausted: bool = ..., rate_limit_service: _Optional[_Union[_rls_pb2.RateLimitServiceConfig, _Mapping]] = ..., enable_x_ratelimit_headers: _Optional[_Union[RateLimit.XRateLimitHeadersRFCVersion, str]] = ..., disable_x_envoy_ratelimited_header: bool = ..., rate_limited_status: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., status_on_error: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., filter_enforced: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., failure_mode_deny_percent: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., rate_limits: _Optional[_Iterable[_Union[_route_components_pb2.RateLimit, _Mapping]]] = ...) -> None: ...

class RateLimitPerRoute(_message.Message):
    __slots__ = ("vh_rate_limits", "override_option", "rate_limits", "domain")
    class VhRateLimitsOptions(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OVERRIDE: _ClassVar[RateLimitPerRoute.VhRateLimitsOptions]
        INCLUDE: _ClassVar[RateLimitPerRoute.VhRateLimitsOptions]
        IGNORE: _ClassVar[RateLimitPerRoute.VhRateLimitsOptions]
    OVERRIDE: RateLimitPerRoute.VhRateLimitsOptions
    INCLUDE: RateLimitPerRoute.VhRateLimitsOptions
    IGNORE: RateLimitPerRoute.VhRateLimitsOptions
    class OverrideOptions(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[RateLimitPerRoute.OverrideOptions]
        OVERRIDE_POLICY: _ClassVar[RateLimitPerRoute.OverrideOptions]
        INCLUDE_POLICY: _ClassVar[RateLimitPerRoute.OverrideOptions]
        IGNORE_POLICY: _ClassVar[RateLimitPerRoute.OverrideOptions]
    DEFAULT: RateLimitPerRoute.OverrideOptions
    OVERRIDE_POLICY: RateLimitPerRoute.OverrideOptions
    INCLUDE_POLICY: RateLimitPerRoute.OverrideOptions
    IGNORE_POLICY: RateLimitPerRoute.OverrideOptions
    VH_RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_OPTION_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    vh_rate_limits: RateLimitPerRoute.VhRateLimitsOptions
    override_option: RateLimitPerRoute.OverrideOptions
    rate_limits: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.RateLimit]
    domain: str
    def __init__(self, vh_rate_limits: _Optional[_Union[RateLimitPerRoute.VhRateLimitsOptions, str]] = ..., override_option: _Optional[_Union[RateLimitPerRoute.OverrideOptions, str]] = ..., rate_limits: _Optional[_Iterable[_Union[_route_components_pb2.RateLimit, _Mapping]]] = ..., domain: _Optional[str] = ...) -> None: ...
