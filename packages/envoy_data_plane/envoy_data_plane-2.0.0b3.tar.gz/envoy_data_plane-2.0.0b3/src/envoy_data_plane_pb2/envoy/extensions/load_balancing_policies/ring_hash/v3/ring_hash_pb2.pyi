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

class RingHash(_message.Message):
    __slots__ = ("hash_function", "minimum_ring_size", "maximum_ring_size", "use_hostname_for_hashing", "hash_balance_factor", "consistent_hashing_lb_config", "locality_weighted_lb_config")
    class HashFunction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT_HASH: _ClassVar[RingHash.HashFunction]
        XX_HASH: _ClassVar[RingHash.HashFunction]
        MURMUR_HASH_2: _ClassVar[RingHash.HashFunction]
    DEFAULT_HASH: RingHash.HashFunction
    XX_HASH: RingHash.HashFunction
    MURMUR_HASH_2: RingHash.HashFunction
    HASH_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_RING_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_RING_SIZE_FIELD_NUMBER: _ClassVar[int]
    USE_HOSTNAME_FOR_HASHING_FIELD_NUMBER: _ClassVar[int]
    HASH_BALANCE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CONSISTENT_HASHING_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_WEIGHTED_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    hash_function: RingHash.HashFunction
    minimum_ring_size: _wrappers_pb2.UInt64Value
    maximum_ring_size: _wrappers_pb2.UInt64Value
    use_hostname_for_hashing: bool
    hash_balance_factor: _wrappers_pb2.UInt32Value
    consistent_hashing_lb_config: _common_pb2.ConsistentHashingLbConfig
    locality_weighted_lb_config: _common_pb2.LocalityLbConfig.LocalityWeightedLbConfig
    def __init__(self, hash_function: _Optional[_Union[RingHash.HashFunction, str]] = ..., minimum_ring_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., maximum_ring_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., use_hostname_for_hashing: bool = ..., hash_balance_factor: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., consistent_hashing_lb_config: _Optional[_Union[_common_pb2.ConsistentHashingLbConfig, _Mapping]] = ..., locality_weighted_lb_config: _Optional[_Union[_common_pb2.LocalityLbConfig.LocalityWeightedLbConfig, _Mapping]] = ...) -> None: ...
