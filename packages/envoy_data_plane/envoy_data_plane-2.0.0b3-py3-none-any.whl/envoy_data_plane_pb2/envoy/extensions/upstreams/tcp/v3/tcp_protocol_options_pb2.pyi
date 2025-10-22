import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TcpProtocolOptions(_message.Message):
    __slots__ = ("idle_timeout",)
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    idle_timeout: _duration_pb2.Duration
    def __init__(self, idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
