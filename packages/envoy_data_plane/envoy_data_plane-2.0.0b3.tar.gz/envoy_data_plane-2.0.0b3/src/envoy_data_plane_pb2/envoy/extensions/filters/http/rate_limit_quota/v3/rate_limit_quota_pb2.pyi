import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from envoy.type.v3 import ratelimit_strategy_pb2 as _ratelimit_strategy_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.rpc import status_pb2 as _status_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2_1
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import status_pb2 as _status_pb2_1_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RateLimitQuotaFilterConfig(_message.Message):
    __slots__ = ("rlqs_server", "domain", "bucket_matchers", "filter_enabled", "filter_enforced", "request_headers_to_add_when_not_enforced")
    RLQS_SERVER_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    BUCKET_MATCHERS_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENFORCED_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_WHEN_NOT_ENFORCED_FIELD_NUMBER: _ClassVar[int]
    rlqs_server: _grpc_service_pb2.GrpcService
    domain: str
    bucket_matchers: _matcher_pb2.Matcher
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    filter_enforced: _base_pb2.RuntimeFractionalPercent
    request_headers_to_add_when_not_enforced: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    def __init__(self, rlqs_server: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., domain: _Optional[str] = ..., bucket_matchers: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., filter_enforced: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., request_headers_to_add_when_not_enforced: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ...) -> None: ...

class RateLimitQuotaOverride(_message.Message):
    __slots__ = ("domain", "bucket_matchers")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    BUCKET_MATCHERS_FIELD_NUMBER: _ClassVar[int]
    domain: str
    bucket_matchers: _matcher_pb2.Matcher
    def __init__(self, domain: _Optional[str] = ..., bucket_matchers: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ...) -> None: ...

class RateLimitQuotaBucketSettings(_message.Message):
    __slots__ = ("bucket_id_builder", "reporting_interval", "deny_response_settings", "no_assignment_behavior", "expired_assignment_behavior")
    class NoAssignmentBehavior(_message.Message):
        __slots__ = ("fallback_rate_limit",)
        FALLBACK_RATE_LIMIT_FIELD_NUMBER: _ClassVar[int]
        fallback_rate_limit: _ratelimit_strategy_pb2.RateLimitStrategy
        def __init__(self, fallback_rate_limit: _Optional[_Union[_ratelimit_strategy_pb2.RateLimitStrategy, _Mapping]] = ...) -> None: ...
    class ExpiredAssignmentBehavior(_message.Message):
        __slots__ = ("expired_assignment_behavior_timeout", "fallback_rate_limit", "reuse_last_assignment")
        class ReuseLastAssignment(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        EXPIRED_ASSIGNMENT_BEHAVIOR_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        FALLBACK_RATE_LIMIT_FIELD_NUMBER: _ClassVar[int]
        REUSE_LAST_ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
        expired_assignment_behavior_timeout: _duration_pb2.Duration
        fallback_rate_limit: _ratelimit_strategy_pb2.RateLimitStrategy
        reuse_last_assignment: RateLimitQuotaBucketSettings.ExpiredAssignmentBehavior.ReuseLastAssignment
        def __init__(self, expired_assignment_behavior_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., fallback_rate_limit: _Optional[_Union[_ratelimit_strategy_pb2.RateLimitStrategy, _Mapping]] = ..., reuse_last_assignment: _Optional[_Union[RateLimitQuotaBucketSettings.ExpiredAssignmentBehavior.ReuseLastAssignment, _Mapping]] = ...) -> None: ...
    class DenyResponseSettings(_message.Message):
        __slots__ = ("http_status", "http_body", "grpc_status", "response_headers_to_add")
        HTTP_STATUS_FIELD_NUMBER: _ClassVar[int]
        HTTP_BODY_FIELD_NUMBER: _ClassVar[int]
        GRPC_STATUS_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        http_status: _http_status_pb2.HttpStatus
        http_body: _wrappers_pb2.BytesValue
        grpc_status: _status_pb2.Status
        response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        def __init__(self, http_status: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., http_body: _Optional[_Union[_wrappers_pb2.BytesValue, _Mapping]] = ..., grpc_status: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ...) -> None: ...
    class BucketIdBuilder(_message.Message):
        __slots__ = ("bucket_id_builder",)
        class ValueBuilder(_message.Message):
            __slots__ = ("string_value", "custom_value")
            STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
            CUSTOM_VALUE_FIELD_NUMBER: _ClassVar[int]
            string_value: str
            custom_value: _extension_pb2.TypedExtensionConfig
            def __init__(self, string_value: _Optional[str] = ..., custom_value: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
        class BucketIdBuilderEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: RateLimitQuotaBucketSettings.BucketIdBuilder.ValueBuilder
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RateLimitQuotaBucketSettings.BucketIdBuilder.ValueBuilder, _Mapping]] = ...) -> None: ...
        BUCKET_ID_BUILDER_FIELD_NUMBER: _ClassVar[int]
        bucket_id_builder: _containers.MessageMap[str, RateLimitQuotaBucketSettings.BucketIdBuilder.ValueBuilder]
        def __init__(self, bucket_id_builder: _Optional[_Mapping[str, RateLimitQuotaBucketSettings.BucketIdBuilder.ValueBuilder]] = ...) -> None: ...
    BUCKET_ID_BUILDER_FIELD_NUMBER: _ClassVar[int]
    REPORTING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    DENY_RESPONSE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    NO_ASSIGNMENT_BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    EXPIRED_ASSIGNMENT_BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    bucket_id_builder: RateLimitQuotaBucketSettings.BucketIdBuilder
    reporting_interval: _duration_pb2.Duration
    deny_response_settings: RateLimitQuotaBucketSettings.DenyResponseSettings
    no_assignment_behavior: RateLimitQuotaBucketSettings.NoAssignmentBehavior
    expired_assignment_behavior: RateLimitQuotaBucketSettings.ExpiredAssignmentBehavior
    def __init__(self, bucket_id_builder: _Optional[_Union[RateLimitQuotaBucketSettings.BucketIdBuilder, _Mapping]] = ..., reporting_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., deny_response_settings: _Optional[_Union[RateLimitQuotaBucketSettings.DenyResponseSettings, _Mapping]] = ..., no_assignment_behavior: _Optional[_Union[RateLimitQuotaBucketSettings.NoAssignmentBehavior, _Mapping]] = ..., expired_assignment_behavior: _Optional[_Union[RateLimitQuotaBucketSettings.ExpiredAssignmentBehavior, _Mapping]] = ...) -> None: ...
