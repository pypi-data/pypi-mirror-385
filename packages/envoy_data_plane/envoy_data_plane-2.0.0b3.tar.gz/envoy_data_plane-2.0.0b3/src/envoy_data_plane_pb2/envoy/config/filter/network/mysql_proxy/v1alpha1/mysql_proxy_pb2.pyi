from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MySQLProxy(_message.Message):
    __slots__ = ("stat_prefix", "access_log")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    access_log: str
    def __init__(self, stat_prefix: _Optional[str] = ..., access_log: _Optional[str] = ...) -> None: ...
