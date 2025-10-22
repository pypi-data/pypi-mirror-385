import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Squash(_message.Message):
    __slots__ = ("cluster", "attachment_template", "request_timeout", "attachment_timeout", "attachment_poll_period")
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_POLL_PERIOD_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    attachment_template: _struct_pb2.Struct
    request_timeout: _duration_pb2.Duration
    attachment_timeout: _duration_pb2.Duration
    attachment_poll_period: _duration_pb2.Duration
    def __init__(self, cluster: _Optional[str] = ..., attachment_template: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., request_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., attachment_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., attachment_poll_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
