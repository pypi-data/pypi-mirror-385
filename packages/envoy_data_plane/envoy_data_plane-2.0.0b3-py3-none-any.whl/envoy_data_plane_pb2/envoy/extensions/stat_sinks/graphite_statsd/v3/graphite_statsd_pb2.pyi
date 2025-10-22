from envoy.config.core.v3 import address_pb2 as _address_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GraphiteStatsdSink(_message.Message):
    __slots__ = ("address", "prefix", "max_bytes_per_datagram")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    MAX_BYTES_PER_DATAGRAM_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    prefix: str
    max_bytes_per_datagram: _wrappers_pb2.UInt64Value
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., prefix: _Optional[str] = ..., max_bytes_per_datagram: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...
