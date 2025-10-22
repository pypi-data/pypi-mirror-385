from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataSourceServerPreferredAddressConfig(_message.Message):
    __slots__ = ("ipv4_config", "ipv6_config")
    class AddressFamilyConfig(_message.Message):
        __slots__ = ("address", "port", "dnat_address")
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        PORT_FIELD_NUMBER: _ClassVar[int]
        DNAT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        address: _base_pb2.DataSource
        port: _base_pb2.DataSource
        dnat_address: _base_pb2.DataSource
        def __init__(self, address: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., port: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., dnat_address: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
    IPV4_CONFIG_FIELD_NUMBER: _ClassVar[int]
    IPV6_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ipv4_config: DataSourceServerPreferredAddressConfig.AddressFamilyConfig
    ipv6_config: DataSourceServerPreferredAddressConfig.AddressFamilyConfig
    def __init__(self, ipv4_config: _Optional[_Union[DataSourceServerPreferredAddressConfig.AddressFamilyConfig, _Mapping]] = ..., ipv6_config: _Optional[_Union[DataSourceServerPreferredAddressConfig.AddressFamilyConfig, _Mapping]] = ...) -> None: ...
