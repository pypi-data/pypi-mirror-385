import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GradientControllerConfig(_message.Message):
    __slots__ = ("sample_aggregate_percentile", "concurrency_limit_params", "min_rtt_calc_params")
    class ConcurrencyLimitCalculationParams(_message.Message):
        __slots__ = ("max_concurrency_limit", "concurrency_update_interval")
        MAX_CONCURRENCY_LIMIT_FIELD_NUMBER: _ClassVar[int]
        CONCURRENCY_UPDATE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        max_concurrency_limit: _wrappers_pb2.UInt32Value
        concurrency_update_interval: _duration_pb2.Duration
        def __init__(self, max_concurrency_limit: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., concurrency_update_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class MinimumRTTCalculationParams(_message.Message):
        __slots__ = ("interval", "fixed_value", "request_count", "jitter", "min_concurrency", "buffer")
        INTERVAL_FIELD_NUMBER: _ClassVar[int]
        FIXED_VALUE_FIELD_NUMBER: _ClassVar[int]
        REQUEST_COUNT_FIELD_NUMBER: _ClassVar[int]
        JITTER_FIELD_NUMBER: _ClassVar[int]
        MIN_CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
        BUFFER_FIELD_NUMBER: _ClassVar[int]
        interval: _duration_pb2.Duration
        fixed_value: _duration_pb2.Duration
        request_count: _wrappers_pb2.UInt32Value
        jitter: _percent_pb2.Percent
        min_concurrency: _wrappers_pb2.UInt32Value
        buffer: _percent_pb2.Percent
        def __init__(self, interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., fixed_value: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., request_count: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., jitter: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., min_concurrency: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., buffer: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ...) -> None: ...
    SAMPLE_AGGREGATE_PERCENTILE_FIELD_NUMBER: _ClassVar[int]
    CONCURRENCY_LIMIT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MIN_RTT_CALC_PARAMS_FIELD_NUMBER: _ClassVar[int]
    sample_aggregate_percentile: _percent_pb2.Percent
    concurrency_limit_params: GradientControllerConfig.ConcurrencyLimitCalculationParams
    min_rtt_calc_params: GradientControllerConfig.MinimumRTTCalculationParams
    def __init__(self, sample_aggregate_percentile: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., concurrency_limit_params: _Optional[_Union[GradientControllerConfig.ConcurrencyLimitCalculationParams, _Mapping]] = ..., min_rtt_calc_params: _Optional[_Union[GradientControllerConfig.MinimumRTTCalculationParams, _Mapping]] = ...) -> None: ...

class AdaptiveConcurrency(_message.Message):
    __slots__ = ("gradient_controller_config", "enabled", "concurrency_limit_exceeded_status")
    GRADIENT_CONTROLLER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCURRENCY_LIMIT_EXCEEDED_STATUS_FIELD_NUMBER: _ClassVar[int]
    gradient_controller_config: GradientControllerConfig
    enabled: _base_pb2.RuntimeFeatureFlag
    concurrency_limit_exceeded_status: _http_status_pb2.HttpStatus
    def __init__(self, gradient_controller_config: _Optional[_Union[GradientControllerConfig, _Mapping]] = ..., enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., concurrency_limit_exceeded_status: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ...) -> None: ...
