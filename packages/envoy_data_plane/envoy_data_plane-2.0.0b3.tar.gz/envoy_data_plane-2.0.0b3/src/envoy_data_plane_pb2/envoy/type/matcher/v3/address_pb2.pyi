from xds.core.v3 import cidr_pb2 as _cidr_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddressMatcher(_message.Message):
    __slots__ = ("ranges",)
    RANGES_FIELD_NUMBER: _ClassVar[int]
    ranges: _containers.RepeatedCompositeFieldContainer[_cidr_pb2.CidrRange]
    def __init__(self, ranges: _Optional[_Iterable[_Union[_cidr_pb2.CidrRange, _Mapping]]] = ...) -> None: ...
