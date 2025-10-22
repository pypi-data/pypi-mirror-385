import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.endpoint.v3 import load_report_pb2 as _load_report_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoadStatsRequest(_message.Message):
    __slots__ = ("node", "cluster_stats")
    NODE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_STATS_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    cluster_stats: _containers.RepeatedCompositeFieldContainer[_load_report_pb2.ClusterStats]
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., cluster_stats: _Optional[_Iterable[_Union[_load_report_pb2.ClusterStats, _Mapping]]] = ...) -> None: ...

class LoadStatsResponse(_message.Message):
    __slots__ = ("clusters", "send_all_clusters", "load_reporting_interval", "report_endpoint_granularity")
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    SEND_ALL_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    LOAD_REPORTING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    REPORT_ENDPOINT_GRANULARITY_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedScalarFieldContainer[str]
    send_all_clusters: bool
    load_reporting_interval: _duration_pb2.Duration
    report_endpoint_granularity: bool
    def __init__(self, clusters: _Optional[_Iterable[str]] = ..., send_all_clusters: bool = ..., load_reporting_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., report_endpoint_granularity: bool = ...) -> None: ...
