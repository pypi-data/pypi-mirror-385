from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.type.v3 import range_pb2 as _range_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpstreamIpPortMatcher(_message.Message):
    __slots__ = ("upstream_ip", "upstream_port_range")
    UPSTREAM_IP_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_PORT_RANGE_FIELD_NUMBER: _ClassVar[int]
    upstream_ip: _address_pb2.CidrRange
    upstream_port_range: _range_pb2.Int64Range
    def __init__(self, upstream_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., upstream_port_range: _Optional[_Union[_range_pb2.Int64Range, _Mapping]] = ...) -> None: ...
