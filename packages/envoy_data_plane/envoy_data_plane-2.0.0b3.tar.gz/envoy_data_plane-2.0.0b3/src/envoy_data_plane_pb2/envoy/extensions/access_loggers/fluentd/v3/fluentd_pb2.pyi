import datetime

from envoy.config.core.v3 import backoff_pb2 as _backoff_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FluentdAccessLogConfig(_message.Message):
    __slots__ = ("cluster", "tag", "stat_prefix", "buffer_flush_interval", "buffer_size_bytes", "record", "retry_options", "formatters")
    class RetryOptions(_message.Message):
        __slots__ = ("max_connect_attempts", "backoff_options")
        MAX_CONNECT_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
        BACKOFF_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        max_connect_attempts: _wrappers_pb2.UInt32Value
        backoff_options: _backoff_pb2.BackoffStrategy
        def __init__(self, max_connect_attempts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., backoff_options: _Optional[_Union[_backoff_pb2.BackoffStrategy, _Mapping]] = ...) -> None: ...
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BUFFER_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    RECORD_FIELD_NUMBER: _ClassVar[int]
    RETRY_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    FORMATTERS_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    tag: str
    stat_prefix: str
    buffer_flush_interval: _duration_pb2.Duration
    buffer_size_bytes: _wrappers_pb2.UInt32Value
    record: _struct_pb2.Struct
    retry_options: FluentdAccessLogConfig.RetryOptions
    formatters: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    def __init__(self, cluster: _Optional[str] = ..., tag: _Optional[str] = ..., stat_prefix: _Optional[str] = ..., buffer_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., buffer_size_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., record: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., retry_options: _Optional[_Union[FluentdAccessLogConfig.RetryOptions, _Mapping]] = ..., formatters: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ...) -> None: ...
