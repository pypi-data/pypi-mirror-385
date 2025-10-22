import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RedisClusterConfig(_message.Message):
    __slots__ = ("cluster_refresh_rate", "cluster_refresh_timeout", "redirect_refresh_interval", "redirect_refresh_threshold", "failure_refresh_threshold", "host_degraded_refresh_threshold")
    CLUSTER_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_REFRESH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_REFRESH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_REFRESH_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REFRESH_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    HOST_DEGRADED_REFRESH_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    cluster_refresh_rate: _duration_pb2.Duration
    cluster_refresh_timeout: _duration_pb2.Duration
    redirect_refresh_interval: _duration_pb2.Duration
    redirect_refresh_threshold: _wrappers_pb2.UInt32Value
    failure_refresh_threshold: int
    host_degraded_refresh_threshold: int
    def __init__(self, cluster_refresh_rate: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., cluster_refresh_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., redirect_refresh_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., redirect_refresh_threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., failure_refresh_threshold: _Optional[int] = ..., host_degraded_refresh_threshold: _Optional[int] = ...) -> None: ...
