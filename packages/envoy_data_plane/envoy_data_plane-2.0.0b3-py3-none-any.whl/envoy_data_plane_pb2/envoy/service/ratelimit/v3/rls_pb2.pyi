import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.extensions.common.ratelimit.v3 import ratelimit_pb2 as _ratelimit_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
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

class RateLimitRequest(_message.Message):
    __slots__ = ("domain", "descriptors", "hits_addend")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    HITS_ADDEND_FIELD_NUMBER: _ClassVar[int]
    domain: str
    descriptors: _containers.RepeatedCompositeFieldContainer[_ratelimit_pb2.RateLimitDescriptor]
    hits_addend: int
    def __init__(self, domain: _Optional[str] = ..., descriptors: _Optional[_Iterable[_Union[_ratelimit_pb2.RateLimitDescriptor, _Mapping]]] = ..., hits_addend: _Optional[int] = ...) -> None: ...

class RateLimitResponse(_message.Message):
    __slots__ = ("overall_code", "statuses", "response_headers_to_add", "request_headers_to_add", "raw_body", "dynamic_metadata", "quota")
    class Code(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[RateLimitResponse.Code]
        OK: _ClassVar[RateLimitResponse.Code]
        OVER_LIMIT: _ClassVar[RateLimitResponse.Code]
    UNKNOWN: RateLimitResponse.Code
    OK: RateLimitResponse.Code
    OVER_LIMIT: RateLimitResponse.Code
    class RateLimit(_message.Message):
        __slots__ = ("name", "requests_per_unit", "unit")
        class Unit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN: _ClassVar[RateLimitResponse.RateLimit.Unit]
            SECOND: _ClassVar[RateLimitResponse.RateLimit.Unit]
            MINUTE: _ClassVar[RateLimitResponse.RateLimit.Unit]
            HOUR: _ClassVar[RateLimitResponse.RateLimit.Unit]
            DAY: _ClassVar[RateLimitResponse.RateLimit.Unit]
            WEEK: _ClassVar[RateLimitResponse.RateLimit.Unit]
            MONTH: _ClassVar[RateLimitResponse.RateLimit.Unit]
            YEAR: _ClassVar[RateLimitResponse.RateLimit.Unit]
        UNKNOWN: RateLimitResponse.RateLimit.Unit
        SECOND: RateLimitResponse.RateLimit.Unit
        MINUTE: RateLimitResponse.RateLimit.Unit
        HOUR: RateLimitResponse.RateLimit.Unit
        DAY: RateLimitResponse.RateLimit.Unit
        WEEK: RateLimitResponse.RateLimit.Unit
        MONTH: RateLimitResponse.RateLimit.Unit
        YEAR: RateLimitResponse.RateLimit.Unit
        NAME_FIELD_NUMBER: _ClassVar[int]
        REQUESTS_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        name: str
        requests_per_unit: int
        unit: RateLimitResponse.RateLimit.Unit
        def __init__(self, name: _Optional[str] = ..., requests_per_unit: _Optional[int] = ..., unit: _Optional[_Union[RateLimitResponse.RateLimit.Unit, str]] = ...) -> None: ...
    class Quota(_message.Message):
        __slots__ = ("requests", "valid_until", "id")
        REQUESTS_FIELD_NUMBER: _ClassVar[int]
        VALID_UNTIL_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        requests: int
        valid_until: _timestamp_pb2.Timestamp
        id: str
        def __init__(self, requests: _Optional[int] = ..., valid_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...
    class DescriptorStatus(_message.Message):
        __slots__ = ("code", "current_limit", "limit_remaining", "duration_until_reset", "quota")
        CODE_FIELD_NUMBER: _ClassVar[int]
        CURRENT_LIMIT_FIELD_NUMBER: _ClassVar[int]
        LIMIT_REMAINING_FIELD_NUMBER: _ClassVar[int]
        DURATION_UNTIL_RESET_FIELD_NUMBER: _ClassVar[int]
        QUOTA_FIELD_NUMBER: _ClassVar[int]
        code: RateLimitResponse.Code
        current_limit: RateLimitResponse.RateLimit
        limit_remaining: int
        duration_until_reset: _duration_pb2.Duration
        quota: RateLimitResponse.Quota
        def __init__(self, code: _Optional[_Union[RateLimitResponse.Code, str]] = ..., current_limit: _Optional[_Union[RateLimitResponse.RateLimit, _Mapping]] = ..., limit_remaining: _Optional[int] = ..., duration_until_reset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., quota: _Optional[_Union[RateLimitResponse.Quota, _Mapping]] = ...) -> None: ...
    OVERALL_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    RAW_BODY_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
    QUOTA_FIELD_NUMBER: _ClassVar[int]
    overall_code: RateLimitResponse.Code
    statuses: _containers.RepeatedCompositeFieldContainer[RateLimitResponse.DescriptorStatus]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
    raw_body: bytes
    dynamic_metadata: _struct_pb2.Struct
    quota: RateLimitResponse.Quota
    def __init__(self, overall_code: _Optional[_Union[RateLimitResponse.Code, str]] = ..., statuses: _Optional[_Iterable[_Union[RateLimitResponse.DescriptorStatus, _Mapping]]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ..., raw_body: _Optional[bytes] = ..., dynamic_metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., quota: _Optional[_Union[RateLimitResponse.Quota, _Mapping]] = ...) -> None: ...
