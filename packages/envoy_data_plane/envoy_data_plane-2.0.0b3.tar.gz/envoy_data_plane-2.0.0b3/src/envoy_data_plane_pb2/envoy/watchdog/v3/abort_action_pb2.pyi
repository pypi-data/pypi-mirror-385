import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AbortActionConfig(_message.Message):
    __slots__ = ("wait_duration",)
    WAIT_DURATION_FIELD_NUMBER: _ClassVar[int]
    wait_duration: _duration_pb2.Duration
    def __init__(self, wait_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
