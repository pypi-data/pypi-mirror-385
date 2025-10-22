import datetime

from envoy.api.v2.ratelimit import ratelimit_pb2 as _ratelimit_pb2
from envoy.config.ratelimit.v2 import rls_pb2 as _rls_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RateLimit(_message.Message):
    __slots__ = ("stat_prefix", "domain", "descriptors", "timeout", "failure_mode_deny", "rate_limit_service")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_DENY_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMIT_SERVICE_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    domain: str
    descriptors: _containers.RepeatedCompositeFieldContainer[_ratelimit_pb2.RateLimitDescriptor]
    timeout: _duration_pb2.Duration
    failure_mode_deny: bool
    rate_limit_service: _rls_pb2.RateLimitServiceConfig
    def __init__(self, stat_prefix: _Optional[str] = ..., domain: _Optional[str] = ..., descriptors: _Optional[_Iterable[_Union[_ratelimit_pb2.RateLimitDescriptor, _Mapping]]] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., failure_mode_deny: bool = ..., rate_limit_service: _Optional[_Union[_rls_pb2.RateLimitServiceConfig, _Mapping]] = ...) -> None: ...
