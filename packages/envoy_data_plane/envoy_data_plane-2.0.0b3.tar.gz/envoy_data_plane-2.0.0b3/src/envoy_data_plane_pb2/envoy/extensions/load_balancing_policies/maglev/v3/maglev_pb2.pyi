from envoy.extensions.load_balancing_policies.common.v3 import common_pb2 as _common_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Maglev(_message.Message):
    __slots__ = ("table_size", "consistent_hashing_lb_config", "locality_weighted_lb_config")
    TABLE_SIZE_FIELD_NUMBER: _ClassVar[int]
    CONSISTENT_HASHING_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_WEIGHTED_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    table_size: _wrappers_pb2.UInt64Value
    consistent_hashing_lb_config: _common_pb2.ConsistentHashingLbConfig
    locality_weighted_lb_config: _common_pb2.LocalityLbConfig.LocalityWeightedLbConfig
    def __init__(self, table_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., consistent_hashing_lb_config: _Optional[_Union[_common_pb2.ConsistentHashingLbConfig, _Mapping]] = ..., locality_weighted_lb_config: _Optional[_Union[_common_pb2.LocalityLbConfig.LocalityWeightedLbConfig, _Mapping]] = ...) -> None: ...
