import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RouteAction(_message.Message):
    __slots__ = ("name", "cluster", "weighted_clusters", "metadata", "per_filter_config", "timeout", "retry_policy")
    class PerFilterConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PER_FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    name: str
    cluster: str
    weighted_clusters: _route_components_pb2.WeightedCluster
    metadata: _base_pb2.Metadata
    per_filter_config: _containers.MessageMap[str, _any_pb2.Any]
    timeout: _duration_pb2.Duration
    retry_policy: _base_pb2.RetryPolicy
    def __init__(self, name: _Optional[str] = ..., cluster: _Optional[str] = ..., weighted_clusters: _Optional[_Union[_route_components_pb2.WeightedCluster, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., per_filter_config: _Optional[_Mapping[str, _any_pb2.Any]] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ...) -> None: ...
