from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AppleDnsResolverConfig(_message.Message):
    __slots__ = ("include_unroutable_families",)
    INCLUDE_UNROUTABLE_FAMILIES_FIELD_NUMBER: _ClassVar[int]
    include_unroutable_families: bool
    def __init__(self, include_unroutable_families: bool = ...) -> None: ...
