from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.extensions.load_balancing_policies.common.v3 import common_pb2 as _common_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LeastRequest(_message.Message):
    __slots__ = ("choice_count", "active_request_bias", "slow_start_config", "locality_lb_config", "enable_full_scan", "selection_method")
    class SelectionMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        N_CHOICES: _ClassVar[LeastRequest.SelectionMethod]
        FULL_SCAN: _ClassVar[LeastRequest.SelectionMethod]
    N_CHOICES: LeastRequest.SelectionMethod
    FULL_SCAN: LeastRequest.SelectionMethod
    CHOICE_COUNT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_REQUEST_BIAS_FIELD_NUMBER: _ClassVar[int]
    SLOW_START_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FULL_SCAN_FIELD_NUMBER: _ClassVar[int]
    SELECTION_METHOD_FIELD_NUMBER: _ClassVar[int]
    choice_count: _wrappers_pb2.UInt32Value
    active_request_bias: _base_pb2.RuntimeDouble
    slow_start_config: _common_pb2.SlowStartConfig
    locality_lb_config: _common_pb2.LocalityLbConfig
    enable_full_scan: _wrappers_pb2.BoolValue
    selection_method: LeastRequest.SelectionMethod
    def __init__(self, choice_count: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., active_request_bias: _Optional[_Union[_base_pb2.RuntimeDouble, _Mapping]] = ..., slow_start_config: _Optional[_Union[_common_pb2.SlowStartConfig, _Mapping]] = ..., locality_lb_config: _Optional[_Union[_common_pb2.LocalityLbConfig, _Mapping]] = ..., enable_full_scan: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., selection_method: _Optional[_Union[LeastRequest.SelectionMethod, str]] = ...) -> None: ...
