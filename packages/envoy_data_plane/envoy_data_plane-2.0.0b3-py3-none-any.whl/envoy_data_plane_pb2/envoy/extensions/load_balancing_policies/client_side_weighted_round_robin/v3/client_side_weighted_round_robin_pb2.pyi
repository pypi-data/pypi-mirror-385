import datetime

from envoy.extensions.load_balancing_policies.common.v3 import common_pb2 as _common_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientSideWeightedRoundRobin(_message.Message):
    __slots__ = ("enable_oob_load_report", "oob_reporting_period", "blackout_period", "weight_expiration_period", "weight_update_period", "error_utilization_penalty", "metric_names_for_computing_utilization", "slow_start_config")
    ENABLE_OOB_LOAD_REPORT_FIELD_NUMBER: _ClassVar[int]
    OOB_REPORTING_PERIOD_FIELD_NUMBER: _ClassVar[int]
    BLACKOUT_PERIOD_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_EXPIRATION_PERIOD_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_UPDATE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    ERROR_UTILIZATION_PENALTY_FIELD_NUMBER: _ClassVar[int]
    METRIC_NAMES_FOR_COMPUTING_UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    SLOW_START_CONFIG_FIELD_NUMBER: _ClassVar[int]
    enable_oob_load_report: _wrappers_pb2.BoolValue
    oob_reporting_period: _duration_pb2.Duration
    blackout_period: _duration_pb2.Duration
    weight_expiration_period: _duration_pb2.Duration
    weight_update_period: _duration_pb2.Duration
    error_utilization_penalty: _wrappers_pb2.FloatValue
    metric_names_for_computing_utilization: _containers.RepeatedScalarFieldContainer[str]
    slow_start_config: _common_pb2.SlowStartConfig
    def __init__(self, enable_oob_load_report: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., oob_reporting_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., blackout_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., weight_expiration_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., weight_update_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., error_utilization_penalty: _Optional[_Union[_wrappers_pb2.FloatValue, _Mapping]] = ..., metric_names_for_computing_utilization: _Optional[_Iterable[str]] = ..., slow_start_config: _Optional[_Union[_common_pb2.SlowStartConfig, _Mapping]] = ...) -> None: ...
