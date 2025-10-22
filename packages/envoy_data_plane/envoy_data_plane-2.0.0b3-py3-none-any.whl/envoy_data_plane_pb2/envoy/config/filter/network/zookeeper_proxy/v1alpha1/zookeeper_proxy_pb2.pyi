from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ZooKeeperProxy(_message.Message):
    __slots__ = ("stat_prefix", "access_log", "max_packet_bytes")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    MAX_PACKET_BYTES_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    access_log: str
    max_packet_bytes: _wrappers_pb2.UInt32Value
    def __init__(self, stat_prefix: _Optional[str] = ..., access_log: _Optional[str] = ..., max_packet_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
