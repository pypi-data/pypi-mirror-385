from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class S2AConfiguration(_message.Message):
    __slots__ = ("s2a_address",)
    S2A_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    s2a_address: str
    def __init__(self, s2a_address: _Optional[str] = ...) -> None: ...
