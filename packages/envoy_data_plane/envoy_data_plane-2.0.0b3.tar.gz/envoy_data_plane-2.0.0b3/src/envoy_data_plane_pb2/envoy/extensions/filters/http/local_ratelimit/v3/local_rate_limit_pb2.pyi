from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.extensions.common.ratelimit.v3 import ratelimit_pb2 as _ratelimit_pb2
from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from envoy.type.v3 import token_bucket_pb2 as _token_bucket_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalRateLimit(_message.Message):
    __slots__ = ("stat_prefix", "status", "token_bucket", "filter_enabled", "filter_enforced", "request_headers_to_add_when_not_enforced", "response_headers_to_add", "descriptors", "stage", "local_rate_limit_per_downstream_connection", "local_cluster_rate_limit", "enable_x_ratelimit_headers", "vh_rate_limits", "always_consume_default_token_bucket", "rate_limited_as_resource_exhausted", "rate_limits", "max_dynamic_descriptors")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BUCKET_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENFORCED_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_WHEN_NOT_ENFORCED_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_RATE_LIMIT_PER_DOWNSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    LOCAL_CLUSTER_RATE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_X_RATELIMIT_HEADERS_FIELD_NUMBER: _ClassVar[int]
    VH_RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    ALWAYS_CONSUME_DEFAULT_TOKEN_BUCKET_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITED_AS_RESOURCE_EXHAUSTED_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITS_FIELD_NUMBER: _ClassVar[int]
    MAX_DYNAMIC_DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    status: _http_status_pb2.HttpStatus
    token_bucket: _token_bucket_pb2.TokenBucket
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    filter_enforced: _base_pb2.RuntimeFractionalPercent
    request_headers_to_add_when_not_enforced: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    descriptors: _containers.RepeatedCompositeFieldContainer[_ratelimit_pb2.LocalRateLimitDescriptor]
    stage: int
    local_rate_limit_per_downstream_connection: bool
    local_cluster_rate_limit: _ratelimit_pb2.LocalClusterRateLimit
    enable_x_ratelimit_headers: _ratelimit_pb2.XRateLimitHeadersRFCVersion
    vh_rate_limits: _ratelimit_pb2.VhRateLimitsOptions
    always_consume_default_token_bucket: _wrappers_pb2.BoolValue
    rate_limited_as_resource_exhausted: bool
    rate_limits: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.RateLimit]
    max_dynamic_descriptors: _wrappers_pb2.UInt32Value
    def __init__(self, stat_prefix: _Optional[str] = ..., status: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., token_bucket: _Optional[_Union[_token_bucket_pb2.TokenBucket, _Mapping]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., filter_enforced: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., request_headers_to_add_when_not_enforced: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., descriptors: _Optional[_Iterable[_Union[_ratelimit_pb2.LocalRateLimitDescriptor, _Mapping]]] = ..., stage: _Optional[int] = ..., local_rate_limit_per_downstream_connection: bool = ..., local_cluster_rate_limit: _Optional[_Union[_ratelimit_pb2.LocalClusterRateLimit, _Mapping]] = ..., enable_x_ratelimit_headers: _Optional[_Union[_ratelimit_pb2.XRateLimitHeadersRFCVersion, str]] = ..., vh_rate_limits: _Optional[_Union[_ratelimit_pb2.VhRateLimitsOptions, str]] = ..., always_consume_default_token_bucket: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., rate_limited_as_resource_exhausted: bool = ..., rate_limits: _Optional[_Iterable[_Union[_route_components_pb2.RateLimit, _Mapping]]] = ..., max_dynamic_descriptors: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
