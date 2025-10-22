from envoy.config.filter.fault.v2 import fault_pb2 as _fault_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MongoProxy(_message.Message):
    __slots__ = ("stat_prefix", "access_log", "delay", "emit_dynamic_metadata")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    DELAY_FIELD_NUMBER: _ClassVar[int]
    EMIT_DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    access_log: str
    delay: _fault_pb2.FaultDelay
    emit_dynamic_metadata: bool
    def __init__(self, stat_prefix: _Optional[str] = ..., access_log: _Optional[str] = ..., delay: _Optional[_Union[_fault_pb2.FaultDelay, _Mapping]] = ..., emit_dynamic_metadata: bool = ...) -> None: ...
