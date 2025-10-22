import datetime

from envoy.config.bootstrap.v2 import bootstrap_pb2 as _bootstrap_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigDump(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, configs: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...

class UpdateFailureState(_message.Message):
    __slots__ = ("failed_configuration", "last_update_attempt", "details")
    FAILED_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    failed_configuration: _any_pb2.Any
    last_update_attempt: _timestamp_pb2.Timestamp
    details: str
    def __init__(self, failed_configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_update_attempt: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., details: _Optional[str] = ...) -> None: ...

class BootstrapConfigDump(_message.Message):
    __slots__ = ("bootstrap", "last_updated")
    BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    bootstrap: _bootstrap_pb2.Bootstrap
    last_updated: _timestamp_pb2.Timestamp
    def __init__(self, bootstrap: _Optional[_Union[_bootstrap_pb2.Bootstrap, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

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
        __slots__ = ("name", "active_state", "warming_state", "draining_state", "error_state")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_STATE_FIELD_NUMBER: _ClassVar[int]
        WARMING_STATE_FIELD_NUMBER: _ClassVar[int]
        DRAINING_STATE_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        name: str
        active_state: ListenersConfigDump.DynamicListenerState
        warming_state: ListenersConfigDump.DynamicListenerState
        draining_state: ListenersConfigDump.DynamicListenerState
        error_state: UpdateFailureState
        def __init__(self, name: _Optional[str] = ..., active_state: _Optional[_Union[ListenersConfigDump.DynamicListenerState, _Mapping]] = ..., warming_state: _Optional[_Union[ListenersConfigDump.DynamicListenerState, _Mapping]] = ..., draining_state: _Optional[_Union[ListenersConfigDump.DynamicListenerState, _Mapping]] = ..., error_state: _Optional[_Union[UpdateFailureState, _Mapping]] = ...) -> None: ...
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
        __slots__ = ("version_info", "cluster", "last_updated")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        cluster: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, version_info: _Optional[str] = ..., cluster: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
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
        __slots__ = ("version_info", "route_config", "last_updated")
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        version_info: str
        route_config: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, version_info: _Optional[str] = ..., route_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
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
        __slots__ = ("name", "version_info", "scoped_route_configs", "last_updated")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        name: str
        version_info: str
        scoped_route_configs: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
        last_updated: _timestamp_pb2.Timestamp
        def __init__(self, name: _Optional[str] = ..., version_info: _Optional[str] = ..., scoped_route_configs: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    INLINE_SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_SCOPED_ROUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    inline_scoped_route_configs: _containers.RepeatedCompositeFieldContainer[ScopedRoutesConfigDump.InlineScopedRouteConfigs]
    dynamic_scoped_route_configs: _containers.RepeatedCompositeFieldContainer[ScopedRoutesConfigDump.DynamicScopedRouteConfigs]
    def __init__(self, inline_scoped_route_configs: _Optional[_Iterable[_Union[ScopedRoutesConfigDump.InlineScopedRouteConfigs, _Mapping]]] = ..., dynamic_scoped_route_configs: _Optional[_Iterable[_Union[ScopedRoutesConfigDump.DynamicScopedRouteConfigs, _Mapping]]] = ...) -> None: ...

class SecretsConfigDump(_message.Message):
    __slots__ = ("static_secrets", "dynamic_active_secrets", "dynamic_warming_secrets")
    class DynamicSecret(_message.Message):
        __slots__ = ("name", "version_info", "last_updated", "secret")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        SECRET_FIELD_NUMBER: _ClassVar[int]
        name: str
        version_info: str
        last_updated: _timestamp_pb2.Timestamp
        secret: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., version_info: _Optional[str] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., secret: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class StaticSecret(_message.Message):
        __slots__ = ("name", "last_updated", "secret")
        NAME_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        SECRET_FIELD_NUMBER: _ClassVar[int]
        name: str
        last_updated: _timestamp_pb2.Timestamp
        secret: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., secret: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    STATIC_SECRETS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_ACTIVE_SECRETS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_WARMING_SECRETS_FIELD_NUMBER: _ClassVar[int]
    static_secrets: _containers.RepeatedCompositeFieldContainer[SecretsConfigDump.StaticSecret]
    dynamic_active_secrets: _containers.RepeatedCompositeFieldContainer[SecretsConfigDump.DynamicSecret]
    dynamic_warming_secrets: _containers.RepeatedCompositeFieldContainer[SecretsConfigDump.DynamicSecret]
    def __init__(self, static_secrets: _Optional[_Iterable[_Union[SecretsConfigDump.StaticSecret, _Mapping]]] = ..., dynamic_active_secrets: _Optional[_Iterable[_Union[SecretsConfigDump.DynamicSecret, _Mapping]]] = ..., dynamic_warming_secrets: _Optional[_Iterable[_Union[SecretsConfigDump.DynamicSecret, _Mapping]]] = ...) -> None: ...
