from envoy.admin.v3 import metrics_pb2 as _metrics_pb2
from envoy.config.cluster.v3 import circuit_breaker_pb2 as _circuit_breaker_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import health_check_pb2 as _health_check_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Clusters(_message.Message):
    __slots__ = ("cluster_statuses",)
    CLUSTER_STATUSES_FIELD_NUMBER: _ClassVar[int]
    cluster_statuses: _containers.RepeatedCompositeFieldContainer[ClusterStatus]
    def __init__(self, cluster_statuses: _Optional[_Iterable[_Union[ClusterStatus, _Mapping]]] = ...) -> None: ...

class ClusterStatus(_message.Message):
    __slots__ = ("name", "added_via_api", "success_rate_ejection_threshold", "host_statuses", "local_origin_success_rate_ejection_threshold", "circuit_breakers", "observability_name", "eds_service_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDED_VIA_API_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_EJECTION_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    HOST_STATUSES_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ORIGIN_SUCCESS_RATE_EJECTION_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_BREAKERS_FIELD_NUMBER: _ClassVar[int]
    OBSERVABILITY_NAME_FIELD_NUMBER: _ClassVar[int]
    EDS_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    added_via_api: bool
    success_rate_ejection_threshold: _percent_pb2.Percent
    host_statuses: _containers.RepeatedCompositeFieldContainer[HostStatus]
    local_origin_success_rate_ejection_threshold: _percent_pb2.Percent
    circuit_breakers: _circuit_breaker_pb2.CircuitBreakers
    observability_name: str
    eds_service_name: str
    def __init__(self, name: _Optional[str] = ..., added_via_api: bool = ..., success_rate_ejection_threshold: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., host_statuses: _Optional[_Iterable[_Union[HostStatus, _Mapping]]] = ..., local_origin_success_rate_ejection_threshold: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., circuit_breakers: _Optional[_Union[_circuit_breaker_pb2.CircuitBreakers, _Mapping]] = ..., observability_name: _Optional[str] = ..., eds_service_name: _Optional[str] = ...) -> None: ...

class HostStatus(_message.Message):
    __slots__ = ("address", "stats", "health_status", "success_rate", "weight", "hostname", "priority", "local_origin_success_rate", "locality")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    HEALTH_STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ORIGIN_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    address: _address_pb2.Address
    stats: _containers.RepeatedCompositeFieldContainer[_metrics_pb2.SimpleMetric]
    health_status: HostHealthStatus
    success_rate: _percent_pb2.Percent
    weight: int
    hostname: str
    priority: int
    local_origin_success_rate: _percent_pb2.Percent
    locality: _base_pb2.Locality
    def __init__(self, address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., stats: _Optional[_Iterable[_Union[_metrics_pb2.SimpleMetric, _Mapping]]] = ..., health_status: _Optional[_Union[HostHealthStatus, _Mapping]] = ..., success_rate: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., weight: _Optional[int] = ..., hostname: _Optional[str] = ..., priority: _Optional[int] = ..., local_origin_success_rate: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., locality: _Optional[_Union[_base_pb2.Locality, _Mapping]] = ...) -> None: ...

class HostHealthStatus(_message.Message):
    __slots__ = ("failed_active_health_check", "failed_outlier_check", "failed_active_degraded_check", "pending_dynamic_removal", "pending_active_hc", "excluded_via_immediate_hc_fail", "active_hc_timeout", "eds_health_status")
    FAILED_ACTIVE_HEALTH_CHECK_FIELD_NUMBER: _ClassVar[int]
    FAILED_OUTLIER_CHECK_FIELD_NUMBER: _ClassVar[int]
    FAILED_ACTIVE_DEGRADED_CHECK_FIELD_NUMBER: _ClassVar[int]
    PENDING_DYNAMIC_REMOVAL_FIELD_NUMBER: _ClassVar[int]
    PENDING_ACTIVE_HC_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_VIA_IMMEDIATE_HC_FAIL_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_HC_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    EDS_HEALTH_STATUS_FIELD_NUMBER: _ClassVar[int]
    failed_active_health_check: bool
    failed_outlier_check: bool
    failed_active_degraded_check: bool
    pending_dynamic_removal: bool
    pending_active_hc: bool
    excluded_via_immediate_hc_fail: bool
    active_hc_timeout: bool
    eds_health_status: _health_check_pb2.HealthStatus
    def __init__(self, failed_active_health_check: bool = ..., failed_outlier_check: bool = ..., failed_active_degraded_check: bool = ..., pending_dynamic_removal: bool = ..., pending_active_hc: bool = ..., excluded_via_immediate_hc_fail: bool = ..., active_hc_timeout: bool = ..., eds_health_status: _Optional[_Union[_health_check_pb2.HealthStatus, str]] = ...) -> None: ...
