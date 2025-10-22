from envoy.extensions.filters.network.thrift_proxy.v3 import thrift_proxy_pb2 as _thrift_proxy_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Thrift(_message.Message):
    __slots__ = ("method_name", "transport", "protocol")
    METHOD_NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    method_name: str
    transport: _thrift_proxy_pb2.TransportType
    protocol: _thrift_proxy_pb2.ProtocolType
    def __init__(self, method_name: _Optional[str] = ..., transport: _Optional[_Union[_thrift_proxy_pb2.TransportType, str]] = ..., protocol: _Optional[_Union[_thrift_proxy_pb2.ProtocolType, str]] = ...) -> None: ...
