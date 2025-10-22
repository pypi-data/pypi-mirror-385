import datetime

from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpstreamLocalityStats(_message.Message):
    __slots__ = ("locality", "total_successful_requests", "total_requests_in_progress", "total_error_requests", "total_issued_requests", "load_metric_stats", "upstream_endpoint_stats", "priority")
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SUCCESSFUL_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REQUESTS_IN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ERROR_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ISSUED_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    LOAD_METRIC_STATS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_ENDPOINT_STATS_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    locality: _base_pb2.Locality
    total_successful_requests: int
    total_requests_in_progress: int
    total_error_requests: int
    total_issued_requests: int
    load_metric_stats: _containers.RepeatedCompositeFieldContainer[EndpointLoadMetricStats]
    upstream_endpoint_stats: _containers.RepeatedCompositeFieldContainer[UpstreamEndpointStats]
    priority: int
    def __init__(self, locality: _Optional[_Union[_base_pb2.Locality, _Mapping]] = ..., total_successful_requests: _Optional[int] = ..., total_requests_in_progress: _Optional[int] = ..., total_error_requests: _Optional[int] = ..., total_issued_requests: _Optional[int] = ..., load_metric_stats: _Optional[_Iterable[_Union[EndpointLoadMetricStats, _Mapping]]] = ..., upstream_endpoint_stats: _Optional[_Iterable[_Union[UpstreamEndpointStats, _Mapping]]] = ..., priority: _Optional[int] = ...) -> None: ...

class UpstreamEndpointStats(_message.Message):
    __slots__ = ("address", "metadata", "total_successful_requests", "total_requests_in_progress", "total_error_requests", "total_issued_requests", "load_metric_stats")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SUCCESSFUL_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REQUESTS_IN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ERROR_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ISSUED_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    LOAD_METRIC_STATS_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    metadata: _struct_pb2.Struct
    total_successful_requests: int
    total_requests_in_progress: int
    total_error_requests: int
    total_issued_requests: int
    load_metric_stats: _containers.RepeatedCompositeFieldContainer[EndpointLoadMetricStats]
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., total_successful_requests: _Optional[int] = ..., total_requests_in_progress: _Optional[int] = ..., total_error_requests: _Optional[int] = ..., total_issued_requests: _Optional[int] = ..., load_metric_stats: _Optional[_Iterable[_Union[EndpointLoadMetricStats, _Mapping]]] = ...) -> None: ...

class EndpointLoadMetricStats(_message.Message):
    __slots__ = ("metric_name", "num_requests_finished_with_metric", "total_metric_value")
    METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
    NUM_REQUESTS_FINISHED_WITH_METRIC_FIELD_NUMBER: _ClassVar[int]
    TOTAL_METRIC_VALUE_FIELD_NUMBER: _ClassVar[int]
    metric_name: str
    num_requests_finished_with_metric: int
    total_metric_value: float
    def __init__(self, metric_name: _Optional[str] = ..., num_requests_finished_with_metric: _Optional[int] = ..., total_metric_value: _Optional[float] = ...) -> None: ...

class ClusterStats(_message.Message):
    __slots__ = ("cluster_name", "cluster_service_name", "upstream_locality_stats", "total_dropped_requests", "dropped_requests", "load_report_interval")
    class DroppedRequests(_message.Message):
        __slots__ = ("category", "dropped_count")
        CATEGORY_FIELD_NUMBER: _ClassVar[int]
        DROPPED_COUNT_FIELD_NUMBER: _ClassVar[int]
        category: str
        dropped_count: int
        def __init__(self, category: _Optional[str] = ..., dropped_count: _Optional[int] = ...) -> None: ...
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_LOCALITY_STATS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DROPPED_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    DROPPED_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    LOAD_REPORT_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    cluster_name: str
    cluster_service_name: str
    upstream_locality_stats: _containers.RepeatedCompositeFieldContainer[UpstreamLocalityStats]
    total_dropped_requests: int
    dropped_requests: _containers.RepeatedCompositeFieldContainer[ClusterStats.DroppedRequests]
    load_report_interval: _duration_pb2.Duration
    def __init__(self, cluster_name: _Optional[str] = ..., cluster_service_name: _Optional[str] = ..., upstream_locality_stats: _Optional[_Iterable[_Union[UpstreamLocalityStats, _Mapping]]] = ..., total_dropped_requests: _Optional[int] = ..., dropped_requests: _Optional[_Iterable[_Union[ClusterStats.DroppedRequests, _Mapping]]] = ..., load_report_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
