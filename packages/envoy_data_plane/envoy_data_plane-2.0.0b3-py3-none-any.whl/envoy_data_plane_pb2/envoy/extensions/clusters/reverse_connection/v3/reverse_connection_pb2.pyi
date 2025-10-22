import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReverseConnectionClusterConfig(_message.Message):
    __slots__ = ("cleanup_interval", "host_id_format")
    CLEANUP_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    HOST_ID_FORMAT_FIELD_NUMBER: _ClassVar[int]
    cleanup_interval: _duration_pb2.Duration
    host_id_format: str
    def __init__(self, cleanup_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., host_id_format: _Optional[str] = ...) -> None: ...
