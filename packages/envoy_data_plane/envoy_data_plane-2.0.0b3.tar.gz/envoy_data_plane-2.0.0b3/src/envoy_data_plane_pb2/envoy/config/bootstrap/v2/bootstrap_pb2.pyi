import datetime

from envoy.api.v2.auth import secret_pb2 as _secret_pb2
from envoy.api.v2 import cluster_pb2 as _cluster_pb2
from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import config_source_pb2 as _config_source_pb2
from envoy.api.v2.core import event_service_config_pb2 as _event_service_config_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2_1
from envoy.api.v2 import listener_pb2 as _listener_pb2
from envoy.config.metrics.v2 import stats_pb2 as _stats_pb2
from envoy.config.overload.v2alpha import overload_pb2 as _overload_pb2
from envoy.config.trace.v2 import http_tracer_pb2 as _http_tracer_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Bootstrap(_message.Message):
    __slots__ = ("node", "static_resources", "dynamic_resources", "cluster_manager", "hds_config", "flags_path", "stats_sinks", "stats_config", "stats_flush_interval", "watchdog", "tracing", "runtime", "layered_runtime", "admin", "overload_manager", "enable_dispatcher_stats", "header_prefix", "stats_server_version_override", "use_tcp_for_dns_lookups")
    class StaticResources(_message.Message):
        __slots__ = ("listeners", "clusters", "secrets")
        LISTENERS_FIELD_NUMBER: _ClassVar[int]
        CLUSTERS_FIELD_NUMBER: _ClassVar[int]
        SECRETS_FIELD_NUMBER: _ClassVar[int]
        listeners: _containers.RepeatedCompositeFieldContainer[_listener_pb2.Listener]
        clusters: _containers.RepeatedCompositeFieldContainer[_cluster_pb2.Cluster]
        secrets: _containers.RepeatedCompositeFieldContainer[_secret_pb2.Secret]
        def __init__(self, listeners: _Optional[_Iterable[_Union[_listener_pb2.Listener, _Mapping]]] = ..., clusters: _Optional[_Iterable[_Union[_cluster_pb2.Cluster, _Mapping]]] = ..., secrets: _Optional[_Iterable[_Union[_secret_pb2.Secret, _Mapping]]] = ...) -> None: ...
    class DynamicResources(_message.Message):
        __slots__ = ("lds_config", "cds_config", "ads_config")
        LDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        CDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        ADS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        lds_config: _config_source_pb2.ConfigSource
        cds_config: _config_source_pb2.ConfigSource
        ads_config: _config_source_pb2.ApiConfigSource
        def __init__(self, lds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., cds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., ads_config: _Optional[_Union[_config_source_pb2.ApiConfigSource, _Mapping]] = ...) -> None: ...
    NODE_FIELD_NUMBER: _ClassVar[int]
    STATIC_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_MANAGER_FIELD_NUMBER: _ClassVar[int]
    HDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FLAGS_PATH_FIELD_NUMBER: _ClassVar[int]
    STATS_SINKS_FIELD_NUMBER: _ClassVar[int]
    STATS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STATS_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    WATCHDOG_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    LAYERED_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ADMIN_FIELD_NUMBER: _ClassVar[int]
    OVERLOAD_MANAGER_FIELD_NUMBER: _ClassVar[int]
    ENABLE_DISPATCHER_STATS_FIELD_NUMBER: _ClassVar[int]
    HEADER_PREFIX_FIELD_NUMBER: _ClassVar[int]
    STATS_SERVER_VERSION_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    USE_TCP_FOR_DNS_LOOKUPS_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    static_resources: Bootstrap.StaticResources
    dynamic_resources: Bootstrap.DynamicResources
    cluster_manager: ClusterManager
    hds_config: _config_source_pb2.ApiConfigSource
    flags_path: str
    stats_sinks: _containers.RepeatedCompositeFieldContainer[_stats_pb2.StatsSink]
    stats_config: _stats_pb2.StatsConfig
    stats_flush_interval: _duration_pb2.Duration
    watchdog: Watchdog
    tracing: _http_tracer_pb2.Tracing
    runtime: Runtime
    layered_runtime: LayeredRuntime
    admin: Admin
    overload_manager: _overload_pb2.OverloadManager
    enable_dispatcher_stats: bool
    header_prefix: str
    stats_server_version_override: _wrappers_pb2.UInt64Value
    use_tcp_for_dns_lookups: bool
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., static_resources: _Optional[_Union[Bootstrap.StaticResources, _Mapping]] = ..., dynamic_resources: _Optional[_Union[Bootstrap.DynamicResources, _Mapping]] = ..., cluster_manager: _Optional[_Union[ClusterManager, _Mapping]] = ..., hds_config: _Optional[_Union[_config_source_pb2.ApiConfigSource, _Mapping]] = ..., flags_path: _Optional[str] = ..., stats_sinks: _Optional[_Iterable[_Union[_stats_pb2.StatsSink, _Mapping]]] = ..., stats_config: _Optional[_Union[_stats_pb2.StatsConfig, _Mapping]] = ..., stats_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., watchdog: _Optional[_Union[Watchdog, _Mapping]] = ..., tracing: _Optional[_Union[_http_tracer_pb2.Tracing, _Mapping]] = ..., runtime: _Optional[_Union[Runtime, _Mapping]] = ..., layered_runtime: _Optional[_Union[LayeredRuntime, _Mapping]] = ..., admin: _Optional[_Union[Admin, _Mapping]] = ..., overload_manager: _Optional[_Union[_overload_pb2.OverloadManager, _Mapping]] = ..., enable_dispatcher_stats: bool = ..., header_prefix: _Optional[str] = ..., stats_server_version_override: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., use_tcp_for_dns_lookups: bool = ...) -> None: ...

class Admin(_message.Message):
    __slots__ = ("access_log_path", "profile_path", "address", "socket_options")
    ACCESS_LOG_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_PATH_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SOCKET_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    access_log_path: str
    profile_path: str
    address: _address_pb2.Address
    socket_options: _containers.RepeatedCompositeFieldContainer[_socket_option_pb2_1.SocketOption]
    def __init__(self, access_log_path: _Optional[str] = ..., profile_path: _Optional[str] = ..., address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., socket_options: _Optional[_Iterable[_Union[_socket_option_pb2_1.SocketOption, _Mapping]]] = ...) -> None: ...

class ClusterManager(_message.Message):
    __slots__ = ("local_cluster_name", "outlier_detection", "upstream_bind_config", "load_stats_config")
    class OutlierDetection(_message.Message):
        __slots__ = ("event_log_path", "event_service")
        EVENT_LOG_PATH_FIELD_NUMBER: _ClassVar[int]
        EVENT_SERVICE_FIELD_NUMBER: _ClassVar[int]
        event_log_path: str
        event_service: _event_service_config_pb2.EventServiceConfig
        def __init__(self, event_log_path: _Optional[str] = ..., event_service: _Optional[_Union[_event_service_config_pb2.EventServiceConfig, _Mapping]] = ...) -> None: ...
    LOCAL_CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    OUTLIER_DETECTION_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_BIND_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LOAD_STATS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    local_cluster_name: str
    outlier_detection: ClusterManager.OutlierDetection
    upstream_bind_config: _address_pb2.BindConfig
    load_stats_config: _config_source_pb2.ApiConfigSource
    def __init__(self, local_cluster_name: _Optional[str] = ..., outlier_detection: _Optional[_Union[ClusterManager.OutlierDetection, _Mapping]] = ..., upstream_bind_config: _Optional[_Union[_address_pb2.BindConfig, _Mapping]] = ..., load_stats_config: _Optional[_Union[_config_source_pb2.ApiConfigSource, _Mapping]] = ...) -> None: ...

class Watchdog(_message.Message):
    __slots__ = ("miss_timeout", "megamiss_timeout", "kill_timeout", "multikill_timeout")
    MISS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MEGAMISS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    KILL_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MULTIKILL_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    miss_timeout: _duration_pb2.Duration
    megamiss_timeout: _duration_pb2.Duration
    kill_timeout: _duration_pb2.Duration
    multikill_timeout: _duration_pb2.Duration
    def __init__(self, miss_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., megamiss_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., kill_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., multikill_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class Runtime(_message.Message):
    __slots__ = ("symlink_root", "subdirectory", "override_subdirectory", "base")
    SYMLINK_ROOT_FIELD_NUMBER: _ClassVar[int]
    SUBDIRECTORY_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_SUBDIRECTORY_FIELD_NUMBER: _ClassVar[int]
    BASE_FIELD_NUMBER: _ClassVar[int]
    symlink_root: str
    subdirectory: str
    override_subdirectory: str
    base: _struct_pb2.Struct
    def __init__(self, symlink_root: _Optional[str] = ..., subdirectory: _Optional[str] = ..., override_subdirectory: _Optional[str] = ..., base: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class RuntimeLayer(_message.Message):
    __slots__ = ("name", "static_layer", "disk_layer", "admin_layer", "rtds_layer")
    class DiskLayer(_message.Message):
        __slots__ = ("symlink_root", "subdirectory", "append_service_cluster")
        SYMLINK_ROOT_FIELD_NUMBER: _ClassVar[int]
        SUBDIRECTORY_FIELD_NUMBER: _ClassVar[int]
        APPEND_SERVICE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
        symlink_root: str
        subdirectory: str
        append_service_cluster: bool
        def __init__(self, symlink_root: _Optional[str] = ..., subdirectory: _Optional[str] = ..., append_service_cluster: bool = ...) -> None: ...
    class AdminLayer(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class RtdsLayer(_message.Message):
        __slots__ = ("name", "rtds_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        RTDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        rtds_config: _config_source_pb2.ConfigSource
        def __init__(self, name: _Optional[str] = ..., rtds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATIC_LAYER_FIELD_NUMBER: _ClassVar[int]
    DISK_LAYER_FIELD_NUMBER: _ClassVar[int]
    ADMIN_LAYER_FIELD_NUMBER: _ClassVar[int]
    RTDS_LAYER_FIELD_NUMBER: _ClassVar[int]
    name: str
    static_layer: _struct_pb2.Struct
    disk_layer: RuntimeLayer.DiskLayer
    admin_layer: RuntimeLayer.AdminLayer
    rtds_layer: RuntimeLayer.RtdsLayer
    def __init__(self, name: _Optional[str] = ..., static_layer: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., disk_layer: _Optional[_Union[RuntimeLayer.DiskLayer, _Mapping]] = ..., admin_layer: _Optional[_Union[RuntimeLayer.AdminLayer, _Mapping]] = ..., rtds_layer: _Optional[_Union[RuntimeLayer.RtdsLayer, _Mapping]] = ...) -> None: ...

class LayeredRuntime(_message.Message):
    __slots__ = ("layers",)
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    layers: _containers.RepeatedCompositeFieldContainer[RuntimeLayer]
    def __init__(self, layers: _Optional[_Iterable[_Union[RuntimeLayer, _Mapping]]] = ...) -> None: ...
