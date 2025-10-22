from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PickFirst(_message.Message):
    __slots__ = ("shuffle_address_list",)
    SHUFFLE_ADDRESS_LIST_FIELD_NUMBER: _ClassVar[int]
    shuffle_address_list: bool
    def __init__(self, shuffle_address_list: bool = ...) -> None: ...
