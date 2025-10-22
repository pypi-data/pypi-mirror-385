from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Http11ProxyUpstreamTransport(_message.Message):
    __slots__ = ("transport_socket",)
    TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
    transport_socket: _base_pb2.TransportSocket
    def __init__(self, transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ...) -> None: ...
