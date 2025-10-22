from envoy.extensions.common.dynamic_forward_proxy.v3 import dns_cache_pb2 as _dns_cache_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("stat_prefix", "dns_cache_config", "buffer_options")
    class BufferOptions(_message.Message):
        __slots__ = ("max_buffered_datagrams", "max_buffered_bytes")
        MAX_BUFFERED_DATAGRAMS_FIELD_NUMBER: _ClassVar[int]
        MAX_BUFFERED_BYTES_FIELD_NUMBER: _ClassVar[int]
        max_buffered_datagrams: _wrappers_pb2.UInt32Value
        max_buffered_bytes: _wrappers_pb2.UInt64Value
        def __init__(self, max_buffered_datagrams: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_buffered_bytes: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    DNS_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    BUFFER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    dns_cache_config: _dns_cache_pb2.DnsCacheConfig
    buffer_options: FilterConfig.BufferOptions
    def __init__(self, stat_prefix: _Optional[str] = ..., dns_cache_config: _Optional[_Union[_dns_cache_pb2.DnsCacheConfig, _Mapping]] = ..., buffer_options: _Optional[_Union[FilterConfig.BufferOptions, _Mapping]] = ...) -> None: ...
