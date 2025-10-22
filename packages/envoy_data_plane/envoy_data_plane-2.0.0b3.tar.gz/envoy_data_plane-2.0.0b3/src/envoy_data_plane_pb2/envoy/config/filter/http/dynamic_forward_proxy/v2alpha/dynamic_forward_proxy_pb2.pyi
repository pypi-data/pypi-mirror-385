from envoy.config.common.dynamic_forward_proxy.v2alpha import dns_cache_pb2 as _dns_cache_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("dns_cache_config",)
    DNS_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    dns_cache_config: _dns_cache_pb2.DnsCacheConfig
    def __init__(self, dns_cache_config: _Optional[_Union[_dns_cache_pb2.DnsCacheConfig, _Mapping]] = ...) -> None: ...

class PerRouteConfig(_message.Message):
    __slots__ = ("host_rewrite", "auto_host_rewrite_header")
    HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    AUTO_HOST_REWRITE_HEADER_FIELD_NUMBER: _ClassVar[int]
    host_rewrite: str
    auto_host_rewrite_header: str
    def __init__(self, host_rewrite: _Optional[str] = ..., auto_host_rewrite_header: _Optional[str] = ...) -> None: ...
