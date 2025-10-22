from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckEventFileSink(_message.Message):
    __slots__ = ("event_log_path",)
    EVENT_LOG_PATH_FIELD_NUMBER: _ClassVar[int]
    event_log_path: str
    def __init__(self, event_log_path: _Optional[str] = ...) -> None: ...
