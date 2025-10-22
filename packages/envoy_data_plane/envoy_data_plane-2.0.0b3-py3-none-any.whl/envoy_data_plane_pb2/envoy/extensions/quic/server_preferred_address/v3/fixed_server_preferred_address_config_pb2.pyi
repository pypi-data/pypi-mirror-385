from envoy.config.core.v3 import address_pb2 as _address_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FixedServerPreferredAddressConfig(_message.Message):
    __slots__ = ("ipv4_address", "ipv4_config", "ipv6_address", "ipv6_config")
    class AddressFamilyConfig(_message.Message):
        __slots__ = ("address", "dnat_address")
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        DNAT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        address: _address_pb2.SocketAddress
        dnat_address: _address_pb2.SocketAddress
        def __init__(self, address: _Optional[_Union[_address_pb2.SocketAddress, _Mapping]] = ..., dnat_address: _Optional[_Union[_address_pb2.SocketAddress, _Mapping]] = ...) -> None: ...
    IPV4_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    IPV4_CONFIG_FIELD_NUMBER: _ClassVar[int]
    IPV6_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    IPV6_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ipv4_address: str
    ipv4_config: FixedServerPreferredAddressConfig.AddressFamilyConfig
    ipv6_address: str
    ipv6_config: FixedServerPreferredAddressConfig.AddressFamilyConfig
    def __init__(self, ipv4_address: _Optional[str] = ..., ipv4_config: _Optional[_Union[FixedServerPreferredAddressConfig.AddressFamilyConfig, _Mapping]] = ..., ipv6_address: _Optional[str] = ..., ipv6_config: _Optional[_Union[FixedServerPreferredAddressConfig.AddressFamilyConfig, _Mapping]] = ...) -> None: ...
