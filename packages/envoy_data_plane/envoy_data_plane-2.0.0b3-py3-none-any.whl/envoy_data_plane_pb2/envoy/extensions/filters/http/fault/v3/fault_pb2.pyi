from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.extensions.filters.common.fault.v3 import fault_pb2 as _fault_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import struct_pb2 as _struct_pb2
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

class FaultAbort(_message.Message):
    __slots__ = ("http_status", "grpc_status", "header_abort", "percentage")
    class HeaderAbort(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    HTTP_STATUS_FIELD_NUMBER: _ClassVar[int]
    GRPC_STATUS_FIELD_NUMBER: _ClassVar[int]
    HEADER_ABORT_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    http_status: int
    grpc_status: int
    header_abort: FaultAbort.HeaderAbort
    percentage: _percent_pb2.FractionalPercent
    def __init__(self, http_status: _Optional[int] = ..., grpc_status: _Optional[int] = ..., header_abort: _Optional[_Union[FaultAbort.HeaderAbort, _Mapping]] = ..., percentage: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ...) -> None: ...

class HTTPFault(_message.Message):
    __slots__ = ("delay", "abort", "upstream_cluster", "headers", "downstream_nodes", "max_active_faults", "response_rate_limit", "delay_percent_runtime", "abort_percent_runtime", "delay_duration_runtime", "abort_http_status_runtime", "max_active_faults_runtime", "response_rate_limit_percent_runtime", "abort_grpc_status_runtime", "disable_downstream_cluster_stats", "filter_metadata")
    DELAY_FIELD_NUMBER: _ClassVar[int]
    ABORT_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_NODES_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIVE_FAULTS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_RATE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    DELAY_PERCENT_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ABORT_PERCENT_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    DELAY_DURATION_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ABORT_HTTP_STATUS_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIVE_FAULTS_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_RATE_LIMIT_PERCENT_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ABORT_GRPC_STATUS_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    DISABLE_DOWNSTREAM_CLUSTER_STATS_FIELD_NUMBER: _ClassVar[int]
    FILTER_METADATA_FIELD_NUMBER: _ClassVar[int]
    delay: _fault_pb2.FaultDelay
    abort: FaultAbort
    upstream_cluster: str
    headers: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    downstream_nodes: _containers.RepeatedScalarFieldContainer[str]
    max_active_faults: _wrappers_pb2.UInt32Value
    response_rate_limit: _fault_pb2.FaultRateLimit
    delay_percent_runtime: str
    abort_percent_runtime: str
    delay_duration_runtime: str
    abort_http_status_runtime: str
    max_active_faults_runtime: str
    response_rate_limit_percent_runtime: str
    abort_grpc_status_runtime: str
    disable_downstream_cluster_stats: bool
    filter_metadata: _struct_pb2.Struct
    def __init__(self, delay: _Optional[_Union[_fault_pb2.FaultDelay, _Mapping]] = ..., abort: _Optional[_Union[FaultAbort, _Mapping]] = ..., upstream_cluster: _Optional[str] = ..., headers: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ..., downstream_nodes: _Optional[_Iterable[str]] = ..., max_active_faults: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., response_rate_limit: _Optional[_Union[_fault_pb2.FaultRateLimit, _Mapping]] = ..., delay_percent_runtime: _Optional[str] = ..., abort_percent_runtime: _Optional[str] = ..., delay_duration_runtime: _Optional[str] = ..., abort_http_status_runtime: _Optional[str] = ..., max_active_faults_runtime: _Optional[str] = ..., response_rate_limit_percent_runtime: _Optional[str] = ..., abort_grpc_status_runtime: _Optional[str] = ..., disable_downstream_cluster_stats: bool = ..., filter_metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
