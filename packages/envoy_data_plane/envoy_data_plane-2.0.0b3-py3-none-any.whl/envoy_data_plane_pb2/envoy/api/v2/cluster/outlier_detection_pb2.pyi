import datetime

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

class OutlierDetection(_message.Message):
    __slots__ = ("consecutive_5xx", "interval", "base_ejection_time", "max_ejection_percent", "enforcing_consecutive_5xx", "enforcing_success_rate", "success_rate_minimum_hosts", "success_rate_request_volume", "success_rate_stdev_factor", "consecutive_gateway_failure", "enforcing_consecutive_gateway_failure", "split_external_local_origin_errors", "consecutive_local_origin_failure", "enforcing_consecutive_local_origin_failure", "enforcing_local_origin_success_rate", "failure_percentage_threshold", "enforcing_failure_percentage", "enforcing_failure_percentage_local_origin", "failure_percentage_minimum_hosts", "failure_percentage_request_volume")
    CONSECUTIVE_5XX_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BASE_EJECTION_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_EJECTION_PERCENT_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_CONSECUTIVE_5XX_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_MINIMUM_HOSTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_REQUEST_VOLUME_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_STDEV_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CONSECUTIVE_GATEWAY_FAILURE_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_CONSECUTIVE_GATEWAY_FAILURE_FIELD_NUMBER: _ClassVar[int]
    SPLIT_EXTERNAL_LOCAL_ORIGIN_ERRORS_FIELD_NUMBER: _ClassVar[int]
    CONSECUTIVE_LOCAL_ORIGIN_FAILURE_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_CONSECUTIVE_LOCAL_ORIGIN_FAILURE_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_LOCAL_ORIGIN_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_PERCENTAGE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_FAILURE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_FAILURE_PERCENTAGE_LOCAL_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    FAILURE_PERCENTAGE_MINIMUM_HOSTS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_PERCENTAGE_REQUEST_VOLUME_FIELD_NUMBER: _ClassVar[int]
    consecutive_5xx: _wrappers_pb2.UInt32Value
    interval: _duration_pb2.Duration
    base_ejection_time: _duration_pb2.Duration
    max_ejection_percent: _wrappers_pb2.UInt32Value
    enforcing_consecutive_5xx: _wrappers_pb2.UInt32Value
    enforcing_success_rate: _wrappers_pb2.UInt32Value
    success_rate_minimum_hosts: _wrappers_pb2.UInt32Value
    success_rate_request_volume: _wrappers_pb2.UInt32Value
    success_rate_stdev_factor: _wrappers_pb2.UInt32Value
    consecutive_gateway_failure: _wrappers_pb2.UInt32Value
    enforcing_consecutive_gateway_failure: _wrappers_pb2.UInt32Value
    split_external_local_origin_errors: bool
    consecutive_local_origin_failure: _wrappers_pb2.UInt32Value
    enforcing_consecutive_local_origin_failure: _wrappers_pb2.UInt32Value
    enforcing_local_origin_success_rate: _wrappers_pb2.UInt32Value
    failure_percentage_threshold: _wrappers_pb2.UInt32Value
    enforcing_failure_percentage: _wrappers_pb2.UInt32Value
    enforcing_failure_percentage_local_origin: _wrappers_pb2.UInt32Value
    failure_percentage_minimum_hosts: _wrappers_pb2.UInt32Value
    failure_percentage_request_volume: _wrappers_pb2.UInt32Value
    def __init__(self, consecutive_5xx: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., base_ejection_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_ejection_percent: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_consecutive_5xx: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_success_rate: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., success_rate_minimum_hosts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., success_rate_request_volume: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., success_rate_stdev_factor: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., consecutive_gateway_failure: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_consecutive_gateway_failure: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., split_external_local_origin_errors: bool = ..., consecutive_local_origin_failure: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_consecutive_local_origin_failure: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_local_origin_success_rate: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., failure_percentage_threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_failure_percentage: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing_failure_percentage_local_origin: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., failure_percentage_minimum_hosts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., failure_percentage_request_volume: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
