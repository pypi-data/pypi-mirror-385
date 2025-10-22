from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DownstreamConnectionsConfig(_message.Message):
    __slots__ = ("max_active_downstream_connections",)
    MAX_ACTIVE_DOWNSTREAM_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    max_active_downstream_connections: int
    def __init__(self, max_active_downstream_connections: _Optional[int] = ...) -> None: ...
