import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BandwidthLimit(_message.Message):
    __slots__ = ("stat_prefix", "enable_mode", "limit_kbps", "fill_interval", "runtime_enabled", "enable_response_trailers", "response_trailer_prefix")
    class EnableMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISABLED: _ClassVar[BandwidthLimit.EnableMode]
        REQUEST: _ClassVar[BandwidthLimit.EnableMode]
        RESPONSE: _ClassVar[BandwidthLimit.EnableMode]
        REQUEST_AND_RESPONSE: _ClassVar[BandwidthLimit.EnableMode]
    DISABLED: BandwidthLimit.EnableMode
    REQUEST: BandwidthLimit.EnableMode
    RESPONSE: BandwidthLimit.EnableMode
    REQUEST_AND_RESPONSE: BandwidthLimit.EnableMode
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ENABLE_MODE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_KBPS_FIELD_NUMBER: _ClassVar[int]
    FILL_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ENABLE_RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TRAILER_PREFIX_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    enable_mode: BandwidthLimit.EnableMode
    limit_kbps: _wrappers_pb2.UInt64Value
    fill_interval: _duration_pb2.Duration
    runtime_enabled: _base_pb2.RuntimeFeatureFlag
    enable_response_trailers: bool
    response_trailer_prefix: str
    def __init__(self, stat_prefix: _Optional[str] = ..., enable_mode: _Optional[_Union[BandwidthLimit.EnableMode, str]] = ..., limit_kbps: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., fill_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., runtime_enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., enable_response_trailers: bool = ..., response_trailer_prefix: _Optional[str] = ...) -> None: ...
