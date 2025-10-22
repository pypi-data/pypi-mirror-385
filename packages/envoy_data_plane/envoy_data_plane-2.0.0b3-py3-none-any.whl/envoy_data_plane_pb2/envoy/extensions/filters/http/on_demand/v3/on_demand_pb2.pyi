import datetime

from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OnDemandCds(_message.Message):
    __slots__ = ("source", "resources_locator", "timeout")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_LOCATOR_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    source: _config_source_pb2.ConfigSource
    resources_locator: str
    timeout: _duration_pb2.Duration
    def __init__(self, source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., resources_locator: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class OnDemand(_message.Message):
    __slots__ = ("odcds",)
    ODCDS_FIELD_NUMBER: _ClassVar[int]
    odcds: OnDemandCds
    def __init__(self, odcds: _Optional[_Union[OnDemandCds, _Mapping]] = ...) -> None: ...

class PerRouteConfig(_message.Message):
    __slots__ = ("odcds",)
    ODCDS_FIELD_NUMBER: _ClassVar[int]
    odcds: OnDemandCds
    def __init__(self, odcds: _Optional[_Union[OnDemandCds, _Mapping]] = ...) -> None: ...
