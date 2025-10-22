import datetime

from envoy.type import percent_pb2 as _percent_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FaultDelay(_message.Message):
    __slots__ = ("type", "fixed_delay", "header_delay", "percentage")
    class FaultDelayType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FIXED: _ClassVar[FaultDelay.FaultDelayType]
    FIXED: FaultDelay.FaultDelayType
    class HeaderDelay(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FIXED_DELAY_FIELD_NUMBER: _ClassVar[int]
    HEADER_DELAY_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    type: FaultDelay.FaultDelayType
    fixed_delay: _duration_pb2.Duration
    header_delay: FaultDelay.HeaderDelay
    percentage: _percent_pb2.FractionalPercent
    def __init__(self, type: _Optional[_Union[FaultDelay.FaultDelayType, str]] = ..., fixed_delay: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., header_delay: _Optional[_Union[FaultDelay.HeaderDelay, _Mapping]] = ..., percentage: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ...) -> None: ...

class FaultRateLimit(_message.Message):
    __slots__ = ("fixed_limit", "header_limit", "percentage")
    class FixedLimit(_message.Message):
        __slots__ = ("limit_kbps",)
        LIMIT_KBPS_FIELD_NUMBER: _ClassVar[int]
        limit_kbps: int
        def __init__(self, limit_kbps: _Optional[int] = ...) -> None: ...
    class HeaderLimit(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FIXED_LIMIT_FIELD_NUMBER: _ClassVar[int]
    HEADER_LIMIT_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    fixed_limit: FaultRateLimit.FixedLimit
    header_limit: FaultRateLimit.HeaderLimit
    percentage: _percent_pb2.FractionalPercent
    def __init__(self, fixed_limit: _Optional[_Union[FaultRateLimit.FixedLimit, _Mapping]] = ..., header_limit: _Optional[_Union[FaultRateLimit.HeaderLimit, _Mapping]] = ..., percentage: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ...) -> None: ...
