import datetime

from envoy.type.v3 import ratelimit_strategy_pb2 as _ratelimit_strategy_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RateLimitQuotaUsageReports(_message.Message):
    __slots__ = ("domain", "bucket_quota_usages")
    class BucketQuotaUsage(_message.Message):
        __slots__ = ("bucket_id", "time_elapsed", "num_requests_allowed", "num_requests_denied")
        BUCKET_ID_FIELD_NUMBER: _ClassVar[int]
        TIME_ELAPSED_FIELD_NUMBER: _ClassVar[int]
        NUM_REQUESTS_ALLOWED_FIELD_NUMBER: _ClassVar[int]
        NUM_REQUESTS_DENIED_FIELD_NUMBER: _ClassVar[int]
        bucket_id: BucketId
        time_elapsed: _duration_pb2.Duration
        num_requests_allowed: int
        num_requests_denied: int
        def __init__(self, bucket_id: _Optional[_Union[BucketId, _Mapping]] = ..., time_elapsed: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., num_requests_allowed: _Optional[int] = ..., num_requests_denied: _Optional[int] = ...) -> None: ...
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    BUCKET_QUOTA_USAGES_FIELD_NUMBER: _ClassVar[int]
    domain: str
    bucket_quota_usages: _containers.RepeatedCompositeFieldContainer[RateLimitQuotaUsageReports.BucketQuotaUsage]
    def __init__(self, domain: _Optional[str] = ..., bucket_quota_usages: _Optional[_Iterable[_Union[RateLimitQuotaUsageReports.BucketQuotaUsage, _Mapping]]] = ...) -> None: ...

class RateLimitQuotaResponse(_message.Message):
    __slots__ = ("bucket_action",)
    class BucketAction(_message.Message):
        __slots__ = ("bucket_id", "quota_assignment_action", "abandon_action")
        class QuotaAssignmentAction(_message.Message):
            __slots__ = ("assignment_time_to_live", "rate_limit_strategy")
            ASSIGNMENT_TIME_TO_LIVE_FIELD_NUMBER: _ClassVar[int]
            RATE_LIMIT_STRATEGY_FIELD_NUMBER: _ClassVar[int]
            assignment_time_to_live: _duration_pb2.Duration
            rate_limit_strategy: _ratelimit_strategy_pb2.RateLimitStrategy
            def __init__(self, assignment_time_to_live: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., rate_limit_strategy: _Optional[_Union[_ratelimit_strategy_pb2.RateLimitStrategy, _Mapping]] = ...) -> None: ...
        class AbandonAction(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        BUCKET_ID_FIELD_NUMBER: _ClassVar[int]
        QUOTA_ASSIGNMENT_ACTION_FIELD_NUMBER: _ClassVar[int]
        ABANDON_ACTION_FIELD_NUMBER: _ClassVar[int]
        bucket_id: BucketId
        quota_assignment_action: RateLimitQuotaResponse.BucketAction.QuotaAssignmentAction
        abandon_action: RateLimitQuotaResponse.BucketAction.AbandonAction
        def __init__(self, bucket_id: _Optional[_Union[BucketId, _Mapping]] = ..., quota_assignment_action: _Optional[_Union[RateLimitQuotaResponse.BucketAction.QuotaAssignmentAction, _Mapping]] = ..., abandon_action: _Optional[_Union[RateLimitQuotaResponse.BucketAction.AbandonAction, _Mapping]] = ...) -> None: ...
    BUCKET_ACTION_FIELD_NUMBER: _ClassVar[int]
    bucket_action: _containers.RepeatedCompositeFieldContainer[RateLimitQuotaResponse.BucketAction]
    def __init__(self, bucket_action: _Optional[_Iterable[_Union[RateLimitQuotaResponse.BucketAction, _Mapping]]] = ...) -> None: ...

class BucketId(_message.Message):
    __slots__ = ("bucket",)
    class BucketEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    bucket: _containers.ScalarMap[str, str]
    def __init__(self, bucket: _Optional[_Mapping[str, str]] = ...) -> None: ...
