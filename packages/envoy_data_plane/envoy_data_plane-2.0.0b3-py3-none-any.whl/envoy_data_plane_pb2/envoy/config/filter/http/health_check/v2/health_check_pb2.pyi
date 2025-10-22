import datetime

from envoy.api.v2.route import route_components_pb2 as _route_components_pb2
from envoy.type import percent_pb2 as _percent_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheck(_message.Message):
    __slots__ = ("pass_through_mode", "cache_time", "cluster_min_healthy_percentages", "headers")
    class ClusterMinHealthyPercentagesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _percent_pb2.Percent
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ...) -> None: ...
    PASS_THROUGH_MODE_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_MIN_HEALTHY_PERCENTAGES_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    pass_through_mode: _wrappers_pb2.BoolValue
    cache_time: _duration_pb2.Duration
    cluster_min_healthy_percentages: _containers.MessageMap[str, _percent_pb2.Percent]
    headers: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    def __init__(self, pass_through_mode: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., cache_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., cluster_min_healthy_percentages: _Optional[_Mapping[str, _percent_pb2.Percent]] = ..., headers: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ...) -> None: ...
