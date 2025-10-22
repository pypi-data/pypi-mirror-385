import datetime

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientResourceStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[ClientResourceStatus]
    REQUESTED: _ClassVar[ClientResourceStatus]
    DOES_NOT_EXIST: _ClassVar[ClientResourceStatus]
    ACKED: _ClassVar[ClientResourceStatus]
    NACKED: _ClassVar[ClientResourceStatus]
    RECEIVED_ERROR: _ClassVar[ClientResourceStatus]
    TIMEOUT: _ClassVar[ClientResourceStatus]
UNKNOWN: ClientResourceStatus
REQUESTED: ClientResourceStatus
DOES_NOT_EXIST: ClientResourceStatus
ACKED: ClientResourceStatus
NACKED: ClientResourceStatus
RECEIVED_ERROR: ClientResourceStatus
TIMEOUT: ClientResourceStatus

class UpdateFailureState(_message.Message):
    __slots__ = ("failed_configuration", "last_update_attempt", "details", "version_info")
    FAILED_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    failed_configuration: _any_pb2.Any
    last_update_attempt: _timestamp_pb2.Timestamp
    details: str
    version_info: str
    def __init__(self, failed_configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_update_attempt: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., details: _Optional[str] = ..., version_info: _Optional[str] = ...) -> None: ...

class ListenersConfigDump(_message.Message):
    __slots__ = ("version_info", "static_listeners", "dynamic_listeners")
    class StaticListener(_message.Message):
        __slots__ = ("listener", "last_updated")
        LISTENER_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        listener: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, listener: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class DynamicListenerState(_message.Message):
        __slots__ = ("version_info", "listener", "last_updated")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        LISTENER_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        listener: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, version_info: _Optional[str] = ..., listener: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class DynamicListener(_message.Message):
        __slots__ = ("name", "active_state", "warming_state", "draining_state", "error_state", "client_status")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_STATE_FIELD_NUMBER: _ClassVar[int]
        WARMING_STATE_FIELD_NUMBER: _ClassVar[int]
        DRAINING_STATE_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        name: str
        active_state: ListenersConfigDump.DynamicListenerState
        warming_state: ListenersConfigDump.DynamicListenerState
        draining_state: ListenersConfigDump.DynamicListenerState
        error_state: UpdateFailureState
        client_status: ClientResourceStatus
        def __init__(self, name: _Optional[str] = ..., active_state: _Optional[_Union[ListenersConfigDump.DynamicListenerState, _Mapping]] = ..., warming_state: _Optional[_Union[ListenersConfigDump.DynamicListenerState, _Mapping]] = ..., draining_state: _Optional[_Union[ListenersConfigDump.DynamicListenerState, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[ClientResourceStatus, str]] = ...) -> None: ...
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    STATIC_LISTENERS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_LISTENERS_FIELD_NUMBER: _ClassVar[int]
    version_info: str
    static_listeners: _containers.RepeatedCompositeFieldContainer[ListenersConfigDump.StaticListener]
    dynamic_listeners: _containers.RepeatedCompositeFieldContainer[ListenersConfigDump.DynamicListener]
    def __init__(self, version_info: _Optional[str] = ..., static_listeners: _Optional[_Iterable[_Union[ListenersConfigDump.StaticListener, _Mapping]]] = ..., dynamic_listeners: _Optional[_Iterable[_Union[ListenersConfigDump.DynamicListener, _Mapping]]] = ...) -> None: ...

class ClustersConfigDump(_message.Message):
    __slots__ = ("version_info", "static_clusters", "dynamic_active_clusters", "dynamic_warming_clusters")
    class StaticCluster(_message.Message):
        __slots__ = ("cluster", "last_updated")
        CLUSTER_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        cluster: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, cluster: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class DynamicCluster(_message.Message):
        __slots__ = ("version_info", "cluster", "last_updated", "error_state", "client_status")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        cluster: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        error_state: UpdateFailureState
        client_status: ClientResourceStatus
        def __init__(self, version_info: _Optional[str] = ..., cluster: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[ClientResourceStatus, str]] = ...) -> None: ...
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    STATIC_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_ACTIVE_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_WARMING_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    version_info: str
    static_clusters: _containers.RepeatedCompositeFieldContainer[ClustersConfigDump.StaticCluster]
    dynamic_active_clusters: _containers.RepeatedCompositeFieldContainer[ClustersConfigDump.DynamicCluster]
    dynamic_warming_clusters: _containers.RepeatedCompositeFieldContainer[ClustersConfigDump.DynamicCluster]
    def __init__(self, version_info: _Optional[str] = ..., static_clusters: _Optional[_Iterable[_Union[ClustersConfigDump.StaticCluster, _Mapping]]] = ..., dynamic_active_clusters: _Optional[_Iterable[_Union[ClustersConfigDump.DynamicCluster, _Mapping]]] = ..., dynamic_warming_clusters: _Optional[_Iterable[_Union[ClustersConfigDump.DynamicCluster, _Mapping]]] = ...) -> None: ...

class RoutesConfigDump(_message.Message):
    __slots__ = ("static_route_configs", "dynamic_route_configs")
    class StaticRouteConfig(_message.Message):
        __slots__ = ("route_config", "last_updated")
        ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        route_config: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, route_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class DynamicRouteConfig(_message.Message):
        __slots__ = ("version_info", "route_config", "last_updated", "error_state", "client_status")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        route_config: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        error_state: UpdateFailureState
        client_status: ClientResourceStatus
        def __init__(self, version_info: _Optional[str] = ..., route_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[ClientResourceStatus, str]] = ...) -> None: ...
    STATIC_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    static_route_configs: _containers.RepeatedCompositeFieldContainer[RoutesConfigDump.StaticRouteConfig]
    dynamic_route_configs: _containers.RepeatedCompositeFieldContainer[RoutesConfigDump.DynamicRouteConfig]
    def __init__(self, static_route_configs: _Optional[_Iterable[_Union[RoutesConfigDump.StaticRouteConfig, _Mapping]]] = ..., dynamic_route_configs: _Optional[_Iterable[_Union[RoutesConfigDump.DynamicRouteConfig, _Mapping]]] = ...) -> None: ...

class ScopedRoutesConfigDump(_message.Message):
    __slots__ = ("inline_scoped_route_configs", "dynamic_scoped_route_configs")
    class InlineScopedRouteConfigs(_message.Message):
        __slots__ = ("name", "scoped_route_configs", "last_updated")
        NAME_FIELD_NUMBER: _ClassVar[int]
        SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        name: str
        scoped_route_configs: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, name: _Optional[str] = ..., scoped_route_configs: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class DynamicScopedRouteConfigs(_message.Message):
        __slots__ = ("name", "version_info", "scoped_route_configs", "last_updated", "error_state", "client_status")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        name: str
        version_info: str
        scoped_route_configs: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
        last_updated: _timestamp_pb2.Timestamp
        error_state: UpdateFailureState
        client_status: ClientResourceStatus
        def __init__(self, name: _Optional[str] = ..., version_info: _Optional[str] = ..., scoped_route_configs: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[ClientResourceStatus, str]] = ...) -> None: ...
    INLINE_SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    inline_scoped_route_configs: _containers.RepeatedCompositeFieldContainer[ScopedRoutesConfigDump.InlineScopedRouteConfigs]
    dynamic_scoped_route_configs: _containers.RepeatedCompositeFieldContainer[ScopedRoutesConfigDump.DynamicScopedRouteConfigs]
    def __init__(self, inline_scoped_route_configs: _Optional[_Iterable[_Union[ScopedRoutesConfigDump.InlineScopedRouteConfigs, _Mapping]]] = ..., dynamic_scoped_route_configs: _Optional[_Iterable[_Union[ScopedRoutesConfigDump.DynamicScopedRouteConfigs, _Mapping]]] = ...) -> None: ...

class EndpointsConfigDump(_message.Message):
    __slots__ = ("static_endpoint_configs", "dynamic_endpoint_configs")
    class StaticEndpointConfig(_message.Message):
        __slots__ = ("endpoint_config", "last_updated")
        ENDPOINT_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        endpoint_config: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, endpoint_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class DynamicEndpointConfig(_message.Message):
        __slots__ = ("version_info", "endpoint_config", "last_updated", "error_state", "client_status")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        ENDPOINT_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        endpoint_config: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        error_state: UpdateFailureState
        client_status: ClientResourceStatus
        def __init__(self, version_info: _Optional[str] = ..., endpoint_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[ClientResourceStatus, str]] = ...) -> None: ...
    STATIC_ENDPOINT_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_ENDPOINT_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    static_endpoint_configs: _containers.RepeatedCompositeFieldContainer[EndpointsConfigDump.StaticEndpointConfig]
    dynamic_endpoint_configs: _containers.RepeatedCompositeFieldContainer[EndpointsConfigDump.DynamicEndpointConfig]
    def __init__(self, static_endpoint_configs: _Optional[_Iterable[_Union[EndpointsConfigDump.StaticEndpointConfig, _Mapping]]] = ..., dynamic_endpoint_configs: _Optional[_Iterable[_Union[EndpointsConfigDump.DynamicEndpointConfig, _Mapping]]] = ...) -> None: ...

class EcdsConfigDump(_message.Message):
    __slots__ = ("ecds_filters",)
    class EcdsFilterConfig(_message.Message):
        __slots__ = ("version_info", "ecds_filter", "last_updated", "error_state", "client_status")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        ECDS_FILTER_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        ecds_filter: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        error_state: UpdateFailureState
        client_status: ClientResourceStatus
        def __init__(self, version_info: _Optional[str] = ..., ecds_filter: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[ClientResourceStatus, str]] = ...) -> None: ...
    ECDS_FILTERS_FIELD_NUMBER: _ClassVar[int]
    ecds_filters: _containers.RepeatedCompositeFieldContainer[EcdsConfigDump.EcdsFilterConfig]
    def __init__(self, ecds_filters: _Optional[_Iterable[_Union[EcdsConfigDump.EcdsFilterConfig, _Mapping]]] = ...) -> None: ...
