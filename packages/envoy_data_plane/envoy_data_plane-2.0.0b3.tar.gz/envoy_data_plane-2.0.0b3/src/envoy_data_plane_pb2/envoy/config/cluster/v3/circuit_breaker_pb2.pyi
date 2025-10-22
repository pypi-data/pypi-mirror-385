from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
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

class CircuitBreakers(_message.Message):
    __slots__ = ("thresholds", "per_host_thresholds")
    class Thresholds(_message.Message):
        __slots__ = ("priority", "max_connections", "max_pending_requests", "max_requests", "max_retries", "retry_budget", "track_remaining", "max_connection_pools")
        class RetryBudget(_message.Message):
            __slots__ = ("budget_percent", "min_retry_concurrency")
            BUDGET_PERCENT_FIELD_NUMBER: _ClassVar[int]
            MIN_RETRY_CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
            budget_percent: _percent_pb2.Percent
            min_retry_concurrency: _wrappers_pb2.UInt32Value
            def __init__(self, budget_percent: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., min_retry_concurrency: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
        PRIORITY_FIELD_NUMBER: _ClassVar[int]
        MAX_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
        MAX_PENDING_REQUESTS_FIELD_NUMBER: _ClassVar[int]
        MAX_REQUESTS_FIELD_NUMBER: _ClassVar[int]
        MAX_RETRIES_FIELD_NUMBER: _ClassVar[int]
        RETRY_BUDGET_FIELD_NUMBER: _ClassVar[int]
        TRACK_REMAINING_FIELD_NUMBER: _ClassVar[int]
        MAX_CONNECTION_POOLS_FIELD_NUMBER: _ClassVar[int]
        priority: _base_pb2.RoutingPriority
        max_connections: _wrappers_pb2.UInt32Value
        max_pending_requests: _wrappers_pb2.UInt32Value
        max_requests: _wrappers_pb2.UInt32Value
        max_retries: _wrappers_pb2.UInt32Value
        retry_budget: CircuitBreakers.Thresholds.RetryBudget
        track_remaining: bool
        max_connection_pools: _wrappers_pb2.UInt32Value
        def __init__(self, priority: _Optional[_Union[_base_pb2.RoutingPriority, str]] = ..., max_connections: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_pending_requests: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_requests: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_retries: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., retry_budget: _Optional[_Union[CircuitBreakers.Thresholds.RetryBudget, _Mapping]] = ..., track_remaining: bool = ..., max_connection_pools: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
    THRESHOLDS_FIELD_NUMBER: _ClassVar[int]
    PER_HOST_THRESHOLDS_FIELD_NUMBER: _ClassVar[int]
    thresholds: _containers.RepeatedCompositeFieldContainer[CircuitBreakers.Thresholds]
    per_host_thresholds: _containers.RepeatedCompositeFieldContainer[CircuitBreakers.Thresholds]
    def __init__(self, thresholds: _Optional[_Iterable[_Union[CircuitBreakers.Thresholds, _Mapping]]] = ..., per_host_thresholds: _Optional[_Iterable[_Union[CircuitBreakers.Thresholds, _Mapping]]] = ...) -> None: ...
