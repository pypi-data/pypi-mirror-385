from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatsSink(_message.Message):
    __slots__ = ("name", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class StatsConfig(_message.Message):
    __slots__ = ("stats_tags", "use_all_default_tags", "stats_matcher", "histogram_bucket_settings")
    STATS_TAGS_FIELD_NUMBER: _ClassVar[int]
    USE_ALL_DEFAULT_TAGS_FIELD_NUMBER: _ClassVar[int]
    STATS_MATCHER_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_BUCKET_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    stats_tags: _containers.RepeatedCompositeFieldContainer[TagSpecifier]
    use_all_default_tags: _wrappers_pb2.BoolValue
    stats_matcher: StatsMatcher
    histogram_bucket_settings: _containers.RepeatedCompositeFieldContainer[HistogramBucketSettings]
    def __init__(self, stats_tags: _Optional[_Iterable[_Union[TagSpecifier, _Mapping]]] = ..., use_all_default_tags: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., stats_matcher: _Optional[_Union[StatsMatcher, _Mapping]] = ..., histogram_bucket_settings: _Optional[_Iterable[_Union[HistogramBucketSettings, _Mapping]]] = ...) -> None: ...

class StatsMatcher(_message.Message):
    __slots__ = ("reject_all", "exclusion_list", "inclusion_list")
    REJECT_ALL_FIELD_NUMBER: _ClassVar[int]
    EXCLUSION_LIST_FIELD_NUMBER: _ClassVar[int]
    INCLUSION_LIST_FIELD_NUMBER: _ClassVar[int]
    reject_all: bool
    exclusion_list: _string_pb2.ListStringMatcher
    inclusion_list: _string_pb2.ListStringMatcher
    def __init__(self, reject_all: bool = ..., exclusion_list: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ..., inclusion_list: _Optional[_Union[_string_pb2.ListStringMatcher, _Mapping]] = ...) -> None: ...

class TagSpecifier(_message.Message):
    __slots__ = ("tag_name", "regex", "fixed_value")
    TAG_NAME_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    FIXED_VALUE_FIELD_NUMBER: _ClassVar[int]
    tag_name: str
    regex: str
    fixed_value: str
    def __init__(self, tag_name: _Optional[str] = ..., regex: _Optional[str] = ..., fixed_value: _Optional[str] = ...) -> None: ...

class HistogramBucketSettings(_message.Message):
    __slots__ = ("match", "buckets", "bins")
    MATCH_FIELD_NUMBER: _ClassVar[int]
    BUCKETS_FIELD_NUMBER: _ClassVar[int]
    BINS_FIELD_NUMBER: _ClassVar[int]
    match: _string_pb2.StringMatcher
    buckets: _containers.RepeatedScalarFieldContainer[float]
    bins: _wrappers_pb2.UInt32Value
    def __init__(self, match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., buckets: _Optional[_Iterable[float]] = ..., bins: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class StatsdSink(_message.Message):
    __slots__ = ("address", "tcp_cluster_name", "prefix")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TCP_CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    tcp_cluster_name: str
    prefix: str
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., tcp_cluster_name: _Optional[str] = ..., prefix: _Optional[str] = ...) -> None: ...

class DogStatsdSink(_message.Message):
    __slots__ = ("address", "prefix", "max_bytes_per_datagram")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    MAX_BYTES_PER_DATAGRAM_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    prefix: str
    max_bytes_per_datagram: _wrappers_pb2.UInt64Value
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., prefix: _Optional[str] = ..., max_bytes_per_datagram: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...

class HystrixSink(_message.Message):
    __slots__ = ("num_buckets",)
    NUM_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    num_buckets: int
    def __init__(self, num_buckets: _Optional[int] = ...) -> None: ...
