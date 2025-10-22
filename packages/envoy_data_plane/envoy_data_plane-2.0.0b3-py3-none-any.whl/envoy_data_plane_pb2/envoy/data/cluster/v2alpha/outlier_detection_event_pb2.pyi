import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OutlierEjectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONSECUTIVE_5XX: _ClassVar[OutlierEjectionType]
    CONSECUTIVE_GATEWAY_FAILURE: _ClassVar[OutlierEjectionType]
    SUCCESS_RATE: _ClassVar[OutlierEjectionType]
    CONSECUTIVE_LOCAL_ORIGIN_FAILURE: _ClassVar[OutlierEjectionType]
    SUCCESS_RATE_LOCAL_ORIGIN: _ClassVar[OutlierEjectionType]
    FAILURE_PERCENTAGE: _ClassVar[OutlierEjectionType]
    FAILURE_PERCENTAGE_LOCAL_ORIGIN: _ClassVar[OutlierEjectionType]

class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EJECT: _ClassVar[Action]
    UNEJECT: _ClassVar[Action]
CONSECUTIVE_5XX: OutlierEjectionType
CONSECUTIVE_GATEWAY_FAILURE: OutlierEjectionType
SUCCESS_RATE: OutlierEjectionType
CONSECUTIVE_LOCAL_ORIGIN_FAILURE: OutlierEjectionType
SUCCESS_RATE_LOCAL_ORIGIN: OutlierEjectionType
FAILURE_PERCENTAGE: OutlierEjectionType
FAILURE_PERCENTAGE_LOCAL_ORIGIN: OutlierEjectionType
EJECT: Action
UNEJECT: Action

class OutlierDetectionEvent(_message.Message):
    __slots__ = ("type", "timestamp", "secs_since_last_action", "cluster_name", "upstream_url", "action", "num_ejections", "enforced", "eject_success_rate_event", "eject_consecutive_event", "eject_failure_percentage_event")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SECS_SINCE_LAST_ACTION_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_URL_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    NUM_EJECTIONS_FIELD_NUMBER: _ClassVar[int]
    ENFORCED_FIELD_NUMBER: _ClassVar[int]
    EJECT_SUCCESS_RATE_EVENT_FIELD_NUMBER: _ClassVar[int]
    EJECT_CONSECUTIVE_EVENT_FIELD_NUMBER: _ClassVar[int]
    EJECT_FAILURE_PERCENTAGE_EVENT_FIELD_NUMBER: _ClassVar[int]
    type: OutlierEjectionType
    timestamp: _timestamp_pb2.Timestamp
    secs_since_last_action: _wrappers_pb2.UInt64Value
    cluster_name: str
    upstream_url: str
    action: Action
    num_ejections: int
    enforced: bool
    eject_success_rate_event: OutlierEjectSuccessRate
    eject_consecutive_event: OutlierEjectConsecutive
    eject_failure_percentage_event: OutlierEjectFailurePercentage
    def __init__(self, type: _Optional[_Union[OutlierEjectionType, str]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., secs_since_last_action: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., cluster_name: _Optional[str] = ..., upstream_url: _Optional[str] = ..., action: _Optional[_Union[Action, str]] = ..., num_ejections: _Optional[int] = ..., enforced: bool = ..., eject_success_rate_event: _Optional[_Union[OutlierEjectSuccessRate, _Mapping]] = ..., eject_consecutive_event: _Optional[_Union[OutlierEjectConsecutive, _Mapping]] = ..., eject_failure_percentage_event: _Optional[_Union[OutlierEjectFailurePercentage, _Mapping]] = ...) -> None: ...

class OutlierEjectSuccessRate(_message.Message):
    __slots__ = ("host_success_rate", "cluster_average_success_rate", "cluster_success_rate_ejection_threshold")
    HOST_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_AVERAGE_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_SUCCESS_RATE_EJECTION_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    host_success_rate: int
    cluster_average_success_rate: int
    cluster_success_rate_ejection_threshold: int
    def __init__(self, host_success_rate: _Optional[int] = ..., cluster_average_success_rate: _Optional[int] = ..., cluster_success_rate_ejection_threshold: _Optional[int] = ...) -> None: ...

class OutlierEjectConsecutive(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OutlierEjectFailurePercentage(_message.Message):
    __slots__ = ("host_success_rate",)
    HOST_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    host_success_rate: int
    def __init__(self, host_success_rate: _Optional[int] = ...) -> None: ...
