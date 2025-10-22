import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpUri(_message.Message):
    __slots__ = ("uri", "cluster", "timeout")
    URI_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    uri: str
    cluster: str
    timeout: _duration_pb2.Duration
    def __init__(self, uri: _Optional[str] = ..., cluster: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
