import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.v3 import range_pb2 as _range_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AdmissionControl(_message.Message):
    __slots__ = ("enabled", "success_criteria", "sampling_window", "aggression", "sr_threshold", "rps_threshold", "max_rejection_probability")
    class SuccessCriteria(_message.Message):
        __slots__ = ("http_criteria", "grpc_criteria")
        class HttpCriteria(_message.Message):
            __slots__ = ("http_success_status",)
            HTTP_SUCCESS_STATUS_FIELD_NUMBER: _ClassVar[int]
            http_success_status: _containers.RepeatedCompositeFieldContainer[_range_pb2.Int32Range]
            def __init__(self, http_success_status: _Optional[_Iterable[_Union[_range_pb2.Int32Range, _Mapping]]] = ...) -> None: ...
        class GrpcCriteria(_message.Message):
            __slots__ = ("grpc_success_status",)
            GRPC_SUCCESS_STATUS_FIELD_NUMBER: _ClassVar[int]
            grpc_success_status: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, grpc_success_status: _Optional[_Iterable[int]] = ...) -> None: ...
        HTTP_CRITERIA_FIELD_NUMBER: _ClassVar[int]
        GRPC_CRITERIA_FIELD_NUMBER: _ClassVar[int]
        http_criteria: AdmissionControl.SuccessCriteria.HttpCriteria
        grpc_criteria: AdmissionControl.SuccessCriteria.GrpcCriteria
        def __init__(self, http_criteria: _Optional[_Union[AdmissionControl.SuccessCriteria.HttpCriteria, _Mapping]] = ..., grpc_criteria: _Optional[_Union[AdmissionControl.SuccessCriteria.GrpcCriteria, _Mapping]] = ...) -> None: ...
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    SAMPLING_WINDOW_FIELD_NUMBER: _ClassVar[int]
    AGGRESSION_FIELD_NUMBER: _ClassVar[int]
    SR_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    RPS_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    MAX_REJECTION_PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    enabled: _base_pb2.RuntimeFeatureFlag
    success_criteria: AdmissionControl.SuccessCriteria
    sampling_window: _duration_pb2.Duration
    aggression: _base_pb2.RuntimeDouble
    sr_threshold: _base_pb2.RuntimePercent
    rps_threshold: _base_pb2.RuntimeUInt32
    max_rejection_probability: _base_pb2.RuntimePercent
    def __init__(self, enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., success_criteria: _Optional[_Union[AdmissionControl.SuccessCriteria, _Mapping]] = ..., sampling_window: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., aggression: _Optional[_Union[_base_pb2.RuntimeDouble, _Mapping]] = ..., sr_threshold: _Optional[_Union[_base_pb2.RuntimePercent, _Mapping]] = ..., rps_threshold: _Optional[_Union[_base_pb2.RuntimeUInt32, _Mapping]] = ..., max_rejection_probability: _Optional[_Union[_base_pb2.RuntimePercent, _Mapping]] = ...) -> None: ...
