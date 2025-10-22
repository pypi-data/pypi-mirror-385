from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.v3 import token_bucket_pb2 as _token_bucket_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalRateLimit(_message.Message):
    __slots__ = ("stat_prefix", "token_bucket", "runtime_enabled", "share_key")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BUCKET_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SHARE_KEY_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    token_bucket: _token_bucket_pb2.TokenBucket
    runtime_enabled: _base_pb2.RuntimeFeatureFlag
    share_key: str
    def __init__(self, stat_prefix: _Optional[str] = ..., token_bucket: _Optional[_Union[_token_bucket_pb2.TokenBucket, _Mapping]] = ..., runtime_enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., share_key: _Optional[str] = ...) -> None: ...
