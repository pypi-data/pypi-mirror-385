import datetime

from envoy.extensions.common.dynamic_forward_proxy.v3 import dns_cache_pb2 as _dns_cache_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("dns_cache_config", "sub_cluster_config", "save_upstream_address", "allow_dynamic_host_from_filter_state")
    DNS_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SUB_CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SAVE_UPSTREAM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_DYNAMIC_HOST_FROM_FILTER_STATE_FIELD_NUMBER: _ClassVar[int]
    dns_cache_config: _dns_cache_pb2.DnsCacheConfig
    sub_cluster_config: SubClusterConfig
    save_upstream_address: bool
    allow_dynamic_host_from_filter_state: bool
    def __init__(self, dns_cache_config: _Optional[_Union[_dns_cache_pb2.DnsCacheConfig, _Mapping]] = ..., sub_cluster_config: _Optional[_Union[SubClusterConfig, _Mapping]] = ..., save_upstream_address: bool = ..., allow_dynamic_host_from_filter_state: bool = ...) -> None: ...

class PerRouteConfig(_message.Message):
    __slots__ = ("host_rewrite_literal", "host_rewrite_header")
    HOST_REWRITE_LITERAL_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_HEADER_FIELD_NUMBER: _ClassVar[int]
    host_rewrite_literal: str
    host_rewrite_header: str
    def __init__(self, host_rewrite_literal: _Optional[str] = ..., host_rewrite_header: _Optional[str] = ...) -> None: ...

class SubClusterConfig(_message.Message):
    __slots__ = ("cluster_init_timeout",)
    CLUSTER_INIT_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    cluster_init_timeout: _duration_pb2.Duration
    def __init__(self, cluster_init_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
