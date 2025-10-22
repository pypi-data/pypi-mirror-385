from envoy.type.v3 import ratelimit_unit_pb2 as _ratelimit_unit_pb2
from envoy.type.v3 import token_bucket_pb2 as _token_bucket_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
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

class XRateLimitHeadersRFCVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OFF: _ClassVar[XRateLimitHeadersRFCVersion]
    DRAFT_VERSION_03: _ClassVar[XRateLimitHeadersRFCVersion]

class VhRateLimitsOptions(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OVERRIDE: _ClassVar[VhRateLimitsOptions]
    INCLUDE: _ClassVar[VhRateLimitsOptions]
    IGNORE: _ClassVar[VhRateLimitsOptions]
OFF: XRateLimitHeadersRFCVersion
DRAFT_VERSION_03: XRateLimitHeadersRFCVersion
OVERRIDE: VhRateLimitsOptions
INCLUDE: VhRateLimitsOptions
IGNORE: VhRateLimitsOptions

class RateLimitDescriptor(_message.Message):
    __slots__ = ("entries", "limit", "hits_addend")
    class Entry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class RateLimitOverride(_message.Message):
        __slots__ = ("requests_per_unit", "unit")
        REQUESTS_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        requests_per_unit: int
        unit: _ratelimit_unit_pb2.RateLimitUnit
        def __init__(self, requests_per_unit: _Optional[int] = ..., unit: _Optional[_Union[_ratelimit_unit_pb2.RateLimitUnit, str]] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    HITS_ADDEND_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[RateLimitDescriptor.Entry]
    limit: RateLimitDescriptor.RateLimitOverride
    hits_addend: _wrappers_pb2.UInt64Value
    def __init__(self, entries: _Optional[_Iterable[_Union[RateLimitDescriptor.Entry, _Mapping]]] = ..., limit: _Optional[_Union[RateLimitDescriptor.RateLimitOverride, _Mapping]] = ..., hits_addend: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...

class LocalRateLimitDescriptor(_message.Message):
    __slots__ = ("entries", "token_bucket")
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BUCKET_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[RateLimitDescriptor.Entry]
    token_bucket: _token_bucket_pb2.TokenBucket
    def __init__(self, entries: _Optional[_Iterable[_Union[RateLimitDescriptor.Entry, _Mapping]]] = ..., token_bucket: _Optional[_Union[_token_bucket_pb2.TokenBucket, _Mapping]] = ...) -> None: ...

class LocalClusterRateLimit(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
