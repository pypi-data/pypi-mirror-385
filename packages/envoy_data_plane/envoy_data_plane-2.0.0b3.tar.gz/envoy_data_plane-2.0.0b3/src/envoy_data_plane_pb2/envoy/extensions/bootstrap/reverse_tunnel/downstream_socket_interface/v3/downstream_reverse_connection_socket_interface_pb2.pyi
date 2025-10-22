from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DownstreamReverseConnectionSocketInterface(_message.Message):
    __slots__ = ("stat_prefix", "enable_detailed_stats")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ENABLE_DETAILED_STATS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    enable_detailed_stats: bool
    def __init__(self, stat_prefix: _Optional[str] = ..., enable_detailed_stats: bool = ...) -> None: ...
