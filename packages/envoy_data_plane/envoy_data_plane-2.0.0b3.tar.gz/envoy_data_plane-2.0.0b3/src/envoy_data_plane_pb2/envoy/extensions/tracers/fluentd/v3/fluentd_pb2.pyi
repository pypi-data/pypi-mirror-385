import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FluentdConfig(_message.Message):
    __slots__ = ("cluster", "tag", "stat_prefix", "buffer_flush_interval", "buffer_size_bytes", "retry_policy")
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BUFFER_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    tag: str
    stat_prefix: str
    buffer_flush_interval: _duration_pb2.Duration
    buffer_size_bytes: _wrappers_pb2.UInt32Value
    retry_policy: _base_pb2.RetryPolicy
    def __init__(self, cluster: _Optional[str] = ..., tag: _Optional[str] = ..., stat_prefix: _Optional[str] = ..., buffer_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., buffer_size_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ...) -> None: ...
