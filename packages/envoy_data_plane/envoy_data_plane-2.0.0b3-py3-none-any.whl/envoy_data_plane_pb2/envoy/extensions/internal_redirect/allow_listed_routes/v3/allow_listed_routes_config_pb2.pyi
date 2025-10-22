from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AllowListedRoutesConfig(_message.Message):
    __slots__ = ("allowed_route_names",)
    ALLOWED_ROUTE_NAMES_FIELD_NUMBER: _ClassVar[int]
    allowed_route_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, allowed_route_names: _Optional[_Iterable[str]] = ...) -> None: ...
