import datetime

from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceMonitor(_message.Message):
    __slots__ = ("name", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ThresholdTrigger(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class ScaledTrigger(_message.Message):
    __slots__ = ("scaling_threshold", "saturation_threshold")
    SCALING_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SATURATION_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    scaling_threshold: float
    saturation_threshold: float
    def __init__(self, scaling_threshold: _Optional[float] = ..., saturation_threshold: _Optional[float] = ...) -> None: ...

class Trigger(_message.Message):
    __slots__ = ("name", "threshold", "scaled")
    NAME_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SCALED_FIELD_NUMBER: _ClassVar[int]
    name: str
    threshold: ThresholdTrigger
    scaled: ScaledTrigger
    def __init__(self, name: _Optional[str] = ..., threshold: _Optional[_Union[ThresholdTrigger, _Mapping]] = ..., scaled: _Optional[_Union[ScaledTrigger, _Mapping]] = ...) -> None: ...

class ScaleTimersOverloadActionConfig(_message.Message):
    __slots__ = ("timer_scale_factors",)
    class TimerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[ScaleTimersOverloadActionConfig.TimerType]
        HTTP_DOWNSTREAM_CONNECTION_IDLE: _ClassVar[ScaleTimersOverloadActionConfig.TimerType]
        HTTP_DOWNSTREAM_STREAM_IDLE: _ClassVar[ScaleTimersOverloadActionConfig.TimerType]
        TRANSPORT_SOCKET_CONNECT: _ClassVar[ScaleTimersOverloadActionConfig.TimerType]
        HTTP_DOWNSTREAM_CONNECTION_MAX: _ClassVar[ScaleTimersOverloadActionConfig.TimerType]
        HTTP_DOWNSTREAM_STREAM_FLUSH: _ClassVar[ScaleTimersOverloadActionConfig.TimerType]
    UNSPECIFIED: ScaleTimersOverloadActionConfig.TimerType
    HTTP_DOWNSTREAM_CONNECTION_IDLE: ScaleTimersOverloadActionConfig.TimerType
    HTTP_DOWNSTREAM_STREAM_IDLE: ScaleTimersOverloadActionConfig.TimerType
    TRANSPORT_SOCKET_CONNECT: ScaleTimersOverloadActionConfig.TimerType
    HTTP_DOWNSTREAM_CONNECTION_MAX: ScaleTimersOverloadActionConfig.TimerType
    HTTP_DOWNSTREAM_STREAM_FLUSH: ScaleTimersOverloadActionConfig.TimerType
    class ScaleTimer(_message.Message):
        __slots__ = ("timer", "min_timeout", "min_scale")
        TIMER_FIELD_NUMBER: _ClassVar[int]
        MIN_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        MIN_SCALE_FIELD_NUMBER: _ClassVar[int]
        timer: ScaleTimersOverloadActionConfig.TimerType
        min_timeout: _duration_pb2.Duration
        min_scale: _percent_pb2.Percent
        def __init__(self, timer: _Optional[_Union[ScaleTimersOverloadActionConfig.TimerType, str]] = ..., min_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., min_scale: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ...) -> None: ...
    TIMER_SCALE_FACTORS_FIELD_NUMBER: _ClassVar[int]
    timer_scale_factors: _containers.RepeatedCompositeFieldContainer[ScaleTimersOverloadActionConfig.ScaleTimer]
    def __init__(self, timer_scale_factors: _Optional[_Iterable[_Union[ScaleTimersOverloadActionConfig.ScaleTimer, _Mapping]]] = ...) -> None: ...

class OverloadAction(_message.Message):
    __slots__ = ("name", "triggers", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    triggers: _containers.RepeatedCompositeFieldContainer[Trigger]
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., triggers: _Optional[_Iterable[_Union[Trigger, _Mapping]]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class LoadShedPoint(_message.Message):
    __slots__ = ("name", "triggers")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    triggers: _containers.RepeatedCompositeFieldContainer[Trigger]
    def __init__(self, name: _Optional[str] = ..., triggers: _Optional[_Iterable[_Union[Trigger, _Mapping]]] = ...) -> None: ...

class BufferFactoryConfig(_message.Message):
    __slots__ = ("minimum_account_to_track_power_of_two",)
    MINIMUM_ACCOUNT_TO_TRACK_POWER_OF_TWO_FIELD_NUMBER: _ClassVar[int]
    minimum_account_to_track_power_of_two: int
    def __init__(self, minimum_account_to_track_power_of_two: _Optional[int] = ...) -> None: ...

class OverloadManager(_message.Message):
    __slots__ = ("refresh_interval", "resource_monitors", "actions", "loadshed_points", "buffer_factory_config")
    REFRESH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_MONITORS_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    LOADSHED_POINTS_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FACTORY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    refresh_interval: _duration_pb2.Duration
    resource_monitors: _containers.RepeatedCompositeFieldContainer[ResourceMonitor]
    actions: _containers.RepeatedCompositeFieldContainer[OverloadAction]
    loadshed_points: _containers.RepeatedCompositeFieldContainer[LoadShedPoint]
    buffer_factory_config: BufferFactoryConfig
    def __init__(self, refresh_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., resource_monitors: _Optional[_Iterable[_Union[ResourceMonitor, _Mapping]]] = ..., actions: _Optional[_Iterable[_Union[OverloadAction, _Mapping]]] = ..., loadshed_points: _Optional[_Iterable[_Union[LoadShedPoint, _Mapping]]] = ..., buffer_factory_config: _Optional[_Union[BufferFactoryConfig, _Mapping]] = ...) -> None: ...
