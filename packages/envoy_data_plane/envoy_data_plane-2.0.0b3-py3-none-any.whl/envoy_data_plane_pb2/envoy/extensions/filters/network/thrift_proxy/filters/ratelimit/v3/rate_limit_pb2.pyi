import datetime

from envoy.config.ratelimit.v3 import rls_pb2 as _rls_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RateLimit(_message.Message):
    __slots__ = ("domain", "stage", "timeout", "failure_mode_deny", "rate_limit_service")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_DENY_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMIT_SERVICE_FIELD_NUMBER: _ClassVar[int]
    domain: str
    stage: int
    timeout: _duration_pb2.Duration
    failure_mode_deny: bool
    rate_limit_service: _rls_pb2.RateLimitServiceConfig
    def __init__(self, domain: _Optional[str] = ..., stage: _Optional[int] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., failure_mode_deny: bool = ..., rate_limit_service: _Optional[_Union[_rls_pb2.RateLimitServiceConfig, _Mapping]] = ...) -> None: ...
