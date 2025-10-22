from envoy.extensions.common.dynamic_forward_proxy.v3 import dns_cache_pb2 as _dns_cache_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("dns_cache_config", "port_value", "save_upstream_address")
    DNS_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PORT_VALUE_FIELD_NUMBER: _ClassVar[int]
    SAVE_UPSTREAM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    dns_cache_config: _dns_cache_pb2.DnsCacheConfig
    port_value: int
    save_upstream_address: bool
    def __init__(self, dns_cache_config: _Optional[_Union[_dns_cache_pb2.DnsCacheConfig, _Mapping]] = ..., port_value: _Optional[int] = ..., save_upstream_address: bool = ...) -> None: ...
