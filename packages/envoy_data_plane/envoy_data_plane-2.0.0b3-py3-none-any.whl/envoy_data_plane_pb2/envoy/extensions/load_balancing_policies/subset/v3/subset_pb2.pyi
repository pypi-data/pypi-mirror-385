from envoy.config.cluster.v3 import cluster_pb2 as _cluster_pb2
from google.protobuf import struct_pb2 as _struct_pb2
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

class Subset(_message.Message):
    __slots__ = ("fallback_policy", "default_subset", "subset_selectors", "allow_redundant_keys", "locality_weight_aware", "scale_locality_weight", "panic_mode_any", "list_as_any", "metadata_fallback_policy", "subset_lb_policy")
    class LbSubsetFallbackPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NO_FALLBACK: _ClassVar[Subset.LbSubsetFallbackPolicy]
        ANY_ENDPOINT: _ClassVar[Subset.LbSubsetFallbackPolicy]
        DEFAULT_SUBSET: _ClassVar[Subset.LbSubsetFallbackPolicy]
    NO_FALLBACK: Subset.LbSubsetFallbackPolicy
    ANY_ENDPOINT: Subset.LbSubsetFallbackPolicy
    DEFAULT_SUBSET: Subset.LbSubsetFallbackPolicy
    class LbSubsetMetadataFallbackPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        METADATA_NO_FALLBACK: _ClassVar[Subset.LbSubsetMetadataFallbackPolicy]
        FALLBACK_LIST: _ClassVar[Subset.LbSubsetMetadataFallbackPolicy]
    METADATA_NO_FALLBACK: Subset.LbSubsetMetadataFallbackPolicy
    FALLBACK_LIST: Subset.LbSubsetMetadataFallbackPolicy
    class LbSubsetSelector(_message.Message):
        __slots__ = ("keys", "single_host_per_subset", "fallback_policy", "fallback_keys_subset")
        class LbSubsetSelectorFallbackPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NOT_DEFINED: _ClassVar[Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
            NO_FALLBACK: _ClassVar[Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
            ANY_ENDPOINT: _ClassVar[Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
            DEFAULT_SUBSET: _ClassVar[Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
            KEYS_SUBSET: _ClassVar[Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
        NOT_DEFINED: Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
        NO_FALLBACK: Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
        ANY_ENDPOINT: Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
        DEFAULT_SUBSET: Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
        KEYS_SUBSET: Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
        KEYS_FIELD_NUMBER: _ClassVar[int]
        SINGLE_HOST_PER_SUBSET_FIELD_NUMBER: _ClassVar[int]
        FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
        FALLBACK_KEYS_SUBSET_FIELD_NUMBER: _ClassVar[int]
        keys: _containers.RepeatedScalarFieldContainer[str]
        single_host_per_subset: bool
        fallback_policy: Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
        fallback_keys_subset: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, keys: _Optional[_Iterable[str]] = ..., single_host_per_subset: bool = ..., fallback_policy: _Optional[_Union[Subset.LbSubsetSelector.LbSubsetSelectorFallbackPolicy, str]] = ..., fallback_keys_subset: _Optional[_Iterable[str]] = ...) -> None: ...
    FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_SUBSET_FIELD_NUMBER: _ClassVar[int]
    SUBSET_SELECTORS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_REDUNDANT_KEYS_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_WEIGHT_AWARE_FIELD_NUMBER: _ClassVar[int]
    SCALE_LOCALITY_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    PANIC_MODE_ANY_FIELD_NUMBER: _ClassVar[int]
    LIST_AS_ANY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
    SUBSET_LB_POLICY_FIELD_NUMBER: _ClassVar[int]
    fallback_policy: Subset.LbSubsetFallbackPolicy
    default_subset: _struct_pb2.Struct
    subset_selectors: _containers.RepeatedCompositeFieldContainer[Subset.LbSubsetSelector]
    allow_redundant_keys: bool
    locality_weight_aware: bool
    scale_locality_weight: bool
    panic_mode_any: bool
    list_as_any: bool
    metadata_fallback_policy: Subset.LbSubsetMetadataFallbackPolicy
    subset_lb_policy: _cluster_pb2.LoadBalancingPolicy
    def __init__(self, fallback_policy: _Optional[_Union[Subset.LbSubsetFallbackPolicy, str]] = ..., default_subset: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., subset_selectors: _Optional[_Iterable[_Union[Subset.LbSubsetSelector, _Mapping]]] = ..., allow_redundant_keys: bool = ..., locality_weight_aware: bool = ..., scale_locality_weight: bool = ..., panic_mode_any: bool = ..., list_as_any: bool = ..., metadata_fallback_policy: _Optional[_Union[Subset.LbSubsetMetadataFallbackPolicy, str]] = ..., subset_lb_policy: _Optional[_Union[_cluster_pb2.LoadBalancingPolicy, _Mapping]] = ...) -> None: ...
