import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DatadogRemoteConfig(_message.Message):
    __slots__ = ("polling_interval",)
    POLLING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    polling_interval: _duration_pb2.Duration
    def __init__(self, polling_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class DatadogConfig(_message.Message):
    __slots__ = ("collector_cluster", "service_name", "collector_hostname", "remote_config")
    COLLECTOR_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    COLLECTOR_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    REMOTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    collector_cluster: str
    service_name: str
    collector_hostname: str
    remote_config: DatadogRemoteConfig
    def __init__(self, collector_cluster: _Optional[str] = ..., service_name: _Optional[str] = ..., collector_hostname: _Optional[str] = ..., remote_config: _Optional[_Union[DatadogRemoteConfig, _Mapping]] = ...) -> None: ...
