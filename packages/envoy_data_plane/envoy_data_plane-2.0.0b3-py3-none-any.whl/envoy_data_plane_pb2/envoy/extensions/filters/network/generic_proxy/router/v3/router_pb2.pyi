from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Router(_message.Message):
    __slots__ = ("bind_upstream_connection",)
    BIND_UPSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    bind_upstream_connection: bool
    def __init__(self, bind_upstream_connection: bool = ...) -> None: ...
