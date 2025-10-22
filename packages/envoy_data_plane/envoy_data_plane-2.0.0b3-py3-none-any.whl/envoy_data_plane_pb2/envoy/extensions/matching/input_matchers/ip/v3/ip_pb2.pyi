from envoy.config.core.v3 import address_pb2 as _address_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ip(_message.Message):
    __slots__ = ("cidr_ranges", "stat_prefix")
    CIDR_RANGES_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    cidr_ranges: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    stat_prefix: str
    def __init__(self, cidr_ranges: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., stat_prefix: _Optional[str] = ...) -> None: ...
