import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import http_uri_pb2 as _http_uri_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GcpAuthnFilterConfig(_message.Message):
    __slots__ = ("http_uri", "retry_policy", "cache_config", "token_header", "cluster", "timeout")
    HTTP_URI_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TOKEN_HEADER_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    http_uri: _http_uri_pb2.HttpUri
    retry_policy: _base_pb2.RetryPolicy
    cache_config: TokenCacheConfig
    token_header: TokenHeader
    cluster: str
    timeout: _duration_pb2.Duration
    def __init__(self, http_uri: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ..., cache_config: _Optional[_Union[TokenCacheConfig, _Mapping]] = ..., token_header: _Optional[_Union[TokenHeader, _Mapping]] = ..., cluster: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class Audience(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class TokenCacheConfig(_message.Message):
    __slots__ = ("cache_size",)
    CACHE_SIZE_FIELD_NUMBER: _ClassVar[int]
    cache_size: _wrappers_pb2.UInt64Value
    def __init__(self, cache_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...

class TokenHeader(_message.Message):
    __slots__ = ("name", "value_prefix")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    name: str
    value_prefix: str
    def __init__(self, name: _Optional[str] = ..., value_prefix: _Optional[str] = ...) -> None: ...
