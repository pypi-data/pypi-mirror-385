import datetime

from envoy.extensions.common.async_files.v3 import async_file_manager_pb2 as _async_file_manager_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileSystemHttpCacheV2Config(_message.Message):
    __slots__ = ("manager_config", "cache_path", "max_cache_size_bytes", "max_individual_cache_entry_size_bytes", "max_cache_entry_count", "cache_subdivisions", "evict_fraction", "max_eviction_period", "min_eviction_period", "create_cache_path")
    MANAGER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CACHE_PATH_FIELD_NUMBER: _ClassVar[int]
    MAX_CACHE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    MAX_INDIVIDUAL_CACHE_ENTRY_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    MAX_CACHE_ENTRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHE_SUBDIVISIONS_FIELD_NUMBER: _ClassVar[int]
    EVICT_FRACTION_FIELD_NUMBER: _ClassVar[int]
    MAX_EVICTION_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MIN_EVICTION_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CREATE_CACHE_PATH_FIELD_NUMBER: _ClassVar[int]
    manager_config: _async_file_manager_pb2.AsyncFileManagerConfig
    cache_path: str
    max_cache_size_bytes: _wrappers_pb2.UInt64Value
    max_individual_cache_entry_size_bytes: _wrappers_pb2.UInt64Value
    max_cache_entry_count: _wrappers_pb2.UInt64Value
    cache_subdivisions: int
    evict_fraction: float
    max_eviction_period: _duration_pb2.Duration
    min_eviction_period: _duration_pb2.Duration
    create_cache_path: bool
    def __init__(self, manager_config: _Optional[_Union[_async_file_manager_pb2.AsyncFileManagerConfig, _Mapping]] = ..., cache_path: _Optional[str] = ..., max_cache_size_bytes: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., max_individual_cache_entry_size_bytes: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., max_cache_entry_count: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., cache_subdivisions: _Optional[int] = ..., evict_fraction: _Optional[float] = ..., max_eviction_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., min_eviction_period: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., create_cache_path: bool = ...) -> None: ...
