from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import proxy_protocol_pb2 as _proxy_protocol_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProxyProtocolUpstreamTransport(_message.Message):
    __slots__ = ("config", "transport_socket", "allow_unspecified_address", "tlv_as_pool_key")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
    ALLOW_UNSPECIFIED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TLV_AS_POOL_KEY_FIELD_NUMBER: _ClassVar[int]
    config: _proxy_protocol_pb2.ProxyProtocolConfig
    transport_socket: _base_pb2.TransportSocket
    allow_unspecified_address: bool
    tlv_as_pool_key: bool
    def __init__(self, config: _Optional[_Union[_proxy_protocol_pb2.ProxyProtocolConfig, _Mapping]] = ..., transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ..., allow_unspecified_address: bool = ..., tlv_as_pool_key: bool = ...) -> None: ...
