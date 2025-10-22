from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpstreamReverseConnectionSocketInterface(_message.Message):
    __slots__ = ("stat_prefix", "ping_failure_threshold", "enable_detailed_stats")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PING_FAILURE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    ENABLE_DETAILED_STATS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    ping_failure_threshold: _wrappers_pb2.UInt32Value
    enable_detailed_stats: bool
    def __init__(self, stat_prefix: _Optional[str] = ..., ping_failure_threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enable_detailed_stats: bool = ...) -> None: ...
