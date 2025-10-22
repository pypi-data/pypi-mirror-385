from envoy.config.core.v3 import base_pb2 as _base_pb2
from io.prometheus.client import metrics_pb2 as _metrics_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamMetricsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamMetricsMessage(_message.Message):
    __slots__ = ("identifier", "envoy_metrics")
    class Identifier(_message.Message):
        __slots__ = ("node",)
        NODE_FIELD_NUMBER: _ClassVar[int]
        node: _base_pb2.Node
        def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ...) -> None: ...
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ENVOY_METRICS_FIELD_NUMBER: _ClassVar[int]
    identifier: StreamMetricsMessage.Identifier
    envoy_metrics: _containers.RepeatedCompositeFieldContainer[_metrics_pb2.MetricFamily]
    def __init__(self, identifier: _Optional[_Union[StreamMetricsMessage.Identifier, _Mapping]] = ..., envoy_metrics: _Optional[_Iterable[_Union[_metrics_pb2.MetricFamily, _Mapping]]] = ...) -> None: ...
