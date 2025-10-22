import datetime

from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckFailureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVE: _ClassVar[HealthCheckFailureType]
    PASSIVE: _ClassVar[HealthCheckFailureType]
    NETWORK: _ClassVar[HealthCheckFailureType]
    NETWORK_TIMEOUT: _ClassVar[HealthCheckFailureType]

class HealthCheckerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HTTP: _ClassVar[HealthCheckerType]
    TCP: _ClassVar[HealthCheckerType]
    GRPC: _ClassVar[HealthCheckerType]
    REDIS: _ClassVar[HealthCheckerType]
    THRIFT: _ClassVar[HealthCheckerType]
ACTIVE: HealthCheckFailureType
PASSIVE: HealthCheckFailureType
NETWORK: HealthCheckFailureType
NETWORK_TIMEOUT: HealthCheckFailureType
HTTP: HealthCheckerType
TCP: HealthCheckerType
GRPC: HealthCheckerType
REDIS: HealthCheckerType
THRIFT: HealthCheckerType

class HealthCheckEvent(_message.Message):
    __slots__ = ("health_checker_type", "host", "cluster_name", "eject_unhealthy_event", "add_healthy_event", "successful_health_check_event", "health_check_failure_event", "degraded_healthy_host", "no_longer_degraded_host", "timestamp", "metadata", "locality")
    HEALTH_CHECKER_TYPE_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    EJECT_UNHEALTHY_EVENT_FIELD_NUMBER: _ClassVar[int]
    ADD_HEALTHY_EVENT_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_HEALTH_CHECK_EVENT_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_FAILURE_EVENT_FIELD_NUMBER: _ClassVar[int]
    DEGRADED_HEALTHY_HOST_FIELD_NUMBER: _ClassVar[int]
    NO_LONGER_DEGRADED_HOST_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    health_checker_type: HealthCheckerType
    host: _address_pb2.Address
    cluster_name: str
    eject_unhealthy_event: HealthCheckEjectUnhealthy
    add_healthy_event: HealthCheckAddHealthy
    successful_health_check_event: HealthCheckSuccessful
    health_check_failure_event: HealthCheckFailure
    degraded_healthy_host: DegradedHealthyHost
    no_longer_degraded_host: NoLongerDegradedHost
    timestamp: _timestamp_pb2.Timestamp
    metadata: _base_pb2.Metadata
    locality: _base_pb2.Locality
    def __init__(self, health_checker_type: _Optional[_Union[HealthCheckerType, str]] = ..., host: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., cluster_name: _Optional[str] = ..., eject_unhealthy_event: _Optional[_Union[HealthCheckEjectUnhealthy, _Mapping]] = ..., add_healthy_event: _Optional[_Union[HealthCheckAddHealthy, _Mapping]] = ..., successful_health_check_event: _Optional[_Union[HealthCheckSuccessful, _Mapping]] = ..., health_check_failure_event: _Optional[_Union[HealthCheckFailure, _Mapping]] = ..., degraded_healthy_host: _Optional[_Union[DegradedHealthyHost, _Mapping]] = ..., no_longer_degraded_host: _Optional[_Union[NoLongerDegradedHost, _Mapping]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., locality: _Optional[_Union[_base_pb2.Locality, _Mapping]] = ...) -> None: ...

class HealthCheckEjectUnhealthy(_message.Message):
    __slots__ = ("failure_type",)
    FAILURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    failure_type: HealthCheckFailureType
    def __init__(self, failure_type: _Optional[_Union[HealthCheckFailureType, str]] = ...) -> None: ...

class HealthCheckAddHealthy(_message.Message):
    __slots__ = ("first_check",)
    FIRST_CHECK_FIELD_NUMBER: _ClassVar[int]
    first_check: bool
    def __init__(self, first_check: bool = ...) -> None: ...

class HealthCheckSuccessful(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckFailure(_message.Message):
    __slots__ = ("failure_type", "first_check")
    FAILURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIRST_CHECK_FIELD_NUMBER: _ClassVar[int]
    failure_type: HealthCheckFailureType
    first_check: bool
    def __init__(self, failure_type: _Optional[_Union[HealthCheckFailureType, str]] = ..., first_check: bool = ...) -> None: ...

class DegradedHealthyHost(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NoLongerDegradedHost(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
