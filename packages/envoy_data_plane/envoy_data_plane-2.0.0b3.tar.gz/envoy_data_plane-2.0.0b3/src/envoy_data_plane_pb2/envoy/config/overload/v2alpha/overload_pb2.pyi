import datetime

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceMonitor(_message.Message):
    __slots__ = ("name", "config", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _struct_pb2.Struct
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ThresholdTrigger(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class Trigger(_message.Message):
    __slots__ = ("name", "threshold")
    NAME_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    name: str
    threshold: ThresholdTrigger
    def __init__(self, name: _Optional[str] = ..., threshold: _Optional[_Union[ThresholdTrigger, _Mapping]] = ...) -> None: ...

class OverloadAction(_message.Message):
    __slots__ = ("name", "triggers")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    triggers: _containers.RepeatedCompositeFieldContainer[Trigger]
    def __init__(self, name: _Optional[str] = ..., triggers: _Optional[_Iterable[_Union[Trigger, _Mapping]]] = ...) -> None: ...

class OverloadManager(_message.Message):
    __slots__ = ("refresh_interval", "resource_monitors", "actions")
    REFRESH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_MONITORS_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    refresh_interval: _duration_pb2.Duration
    resource_monitors: _containers.RepeatedCompositeFieldContainer[ResourceMonitor]
    actions: _containers.RepeatedCompositeFieldContainer[OverloadAction]
    def __init__(self, refresh_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., resource_monitors: _Optional[_Iterable[_Union[ResourceMonitor, _Mapping]]] = ..., actions: _Optional[_Iterable[_Union[OverloadAction, _Mapping]]] = ...) -> None: ...
