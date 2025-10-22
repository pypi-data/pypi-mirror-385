import datetime

from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.cluster.v3 import cluster_pb2 as _cluster_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import event_service_config_pb2 as _event_service_config_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import resolver_pb2 as _resolver_pb2
from envoy.config.core.v3 import socket_option_pb2 as _socket_option_pb2
from envoy.config.listener.v3 import listener_pb2 as _listener_pb2
from envoy.config.metrics.v3 import stats_pb2 as _stats_pb2
from envoy.config.overload.v3 import overload_pb2 as _overload_pb2
from envoy.config.trace.v3 import http_tracer_pb2 as _http_tracer_pb2
from envoy.extensions.transport_sockets.tls.v3 import secret_pb2 as _secret_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import security_pb2 as _security_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Bootstrap(_message.Message):
    __slots__ = ("node", "node_context_params", "static_resources", "dynamic_resources", "cluster_manager", "hds_config", "flags_path", "stats_sinks", "deferred_stat_options", "stats_config", "stats_flush_interval", "stats_flush_on_admin", "stats_eviction_interval", "watchdog", "watchdogs", "tracing", "layered_runtime", "admin", "overload_manager", "enable_dispatcher_stats", "header_prefix", "stats_server_version_override", "use_tcp_for_dns_lookups", "dns_resolution_config", "typed_dns_resolver_config", "bootstrap_extensions", "fatal_actions", "config_sources", "default_config_source", "default_socket_interface", "certificate_provider_instances", "inline_headers", "perf_tracing_file_path", "default_regex_engine", "xds_delegate_extension", "xds_config_tracker_extension", "listener_manager", "application_log_config", "grpc_async_client_manager_config", "memory_allocator_manager")
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
        __slots__ = ("lds_config", "lds_resources_locator", "cds_config", "cds_resources_locator", "ads_config")
        LDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LDS_RESOURCES_LOCATOR_FIELD_NUMBER: _ClassVar[int]
        CDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        CDS_RESOURCES_LOCATOR_FIELD_NUMBER: _ClassVar[int]
        ADS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        lds_config: _config_source_pb2.ConfigSource
        lds_resources_locator: str
        cds_config: _config_source_pb2.ConfigSource
        cds_resources_locator: str
        ads_config: _config_source_pb2.ApiConfigSource
        def __init__(self, lds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., lds_resources_locator: _Optional[str] = ..., cds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., cds_resources_locator: _Optional[str] = ..., ads_config: _Optional[_Union[_config_source_pb2.ApiConfigSource, _Mapping]] = ...) -> None: ...
    class ApplicationLogConfig(_message.Message):
        __slots__ = ("log_format",)
        class LogFormat(_message.Message):
            __slots__ = ("json_format", "text_format")
            JSON_FORMAT_FIELD_NUMBER: _ClassVar[int]
            TEXT_FORMAT_FIELD_NUMBER: _ClassVar[int]
            json_format: _struct_pb2.Struct
            text_format: str
            def __init__(self, json_format: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., text_format: _Optional[str] = ...) -> None: ...
        LOG_FORMAT_FIELD_NUMBER: _ClassVar[int]
        log_format: Bootstrap.ApplicationLogConfig.LogFormat
        def __init__(self, log_format: _Optional[_Union[Bootstrap.ApplicationLogConfig.LogFormat, _Mapping]] = ...) -> None: ...
    class DeferredStatOptions(_message.Message):
        __slots__ = ("enable_deferred_creation_stats",)
        ENABLE_DEFERRED_CREATION_STATS_FIELD_NUMBER: _ClassVar[int]
        enable_deferred_creation_stats: bool
        def __init__(self, enable_deferred_creation_stats: bool = ...) -> None: ...
    class GrpcAsyncClientManagerConfig(_message.Message):
        __slots__ = ("max_cached_entry_idle_duration",)
        MAX_CACHED_ENTRY_IDLE_DURATION_FIELD_NUMBER: _ClassVar[int]
        max_cached_entry_idle_duration: _duration_pb2.Duration
        def __init__(self, max_cached_entry_idle_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class CertificateProviderInstancesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _extension_pb2.TypedExtensionConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
    NODE_FIELD_NUMBER: _ClassVar[int]
    NODE_CONTEXT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    STATIC_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_MANAGER_FIELD_NUMBER: _ClassVar[int]
    HDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FLAGS_PATH_FIELD_NUMBER: _ClassVar[int]
    STATS_SINKS_FIELD_NUMBER: _ClassVar[int]
    DEFERRED_STAT_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    STATS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STATS_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    STATS_FLUSH_ON_ADMIN_FIELD_NUMBER: _ClassVar[int]
    STATS_EVICTION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    WATCHDOG_FIELD_NUMBER: _ClassVar[int]
    WATCHDOGS_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    LAYERED_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ADMIN_FIELD_NUMBER: _ClassVar[int]
    OVERLOAD_MANAGER_FIELD_NUMBER: _ClassVar[int]
    ENABLE_DISPATCHER_STATS_FIELD_NUMBER: _ClassVar[int]
    HEADER_PREFIX_FIELD_NUMBER: _ClassVar[int]
    STATS_SERVER_VERSION_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    USE_TCP_FOR_DNS_LOOKUPS_FIELD_NUMBER: _ClassVar[int]
    DNS_RESOLUTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_DNS_RESOLVER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    FATAL_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_SOURCES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_SOCKET_INTERFACE_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_PROVIDER_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    INLINE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    PERF_TRACING_FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_REGEX_ENGINE_FIELD_NUMBER: _ClassVar[int]
    XDS_DELEGATE_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    XDS_CONFIG_TRACKER_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    LISTENER_MANAGER_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_LOG_CONFIG_FIELD_NUMBER: _ClassVar[int]
    GRPC_ASYNC_CLIENT_MANAGER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    MEMORY_ALLOCATOR_MANAGER_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    node_context_params: _containers.RepeatedScalarFieldContainer[str]
    static_resources: Bootstrap.StaticResources
    dynamic_resources: Bootstrap.DynamicResources
    cluster_manager: ClusterManager
    hds_config: _config_source_pb2.ApiConfigSource
    flags_path: str
    stats_sinks: _containers.RepeatedCompositeFieldContainer[_stats_pb2.StatsSink]
    deferred_stat_options: Bootstrap.DeferredStatOptions
    stats_config: _stats_pb2.StatsConfig
    stats_flush_interval: _duration_pb2.Duration
    stats_flush_on_admin: bool
    stats_eviction_interval: _duration_pb2.Duration
    watchdog: Watchdog
    watchdogs: Watchdogs
    tracing: _http_tracer_pb2.Tracing
    layered_runtime: LayeredRuntime
    admin: Admin
    overload_manager: _overload_pb2.OverloadManager
    enable_dispatcher_stats: bool
    header_prefix: str
    stats_server_version_override: _wrappers_pb2.UInt64Value
    use_tcp_for_dns_lookups: bool
    dns_resolution_config: _resolver_pb2.DnsResolutionConfig
    typed_dns_resolver_config: _extension_pb2.TypedExtensionConfig
    bootstrap_extensions: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    fatal_actions: _containers.RepeatedCompositeFieldContainer[FatalAction]
    config_sources: _containers.RepeatedCompositeFieldContainer[_config_source_pb2.ConfigSource]
    default_config_source: _config_source_pb2.ConfigSource
    default_socket_interface: str
    certificate_provider_instances: _containers.MessageMap[str, _extension_pb2.TypedExtensionConfig]
    inline_headers: _containers.RepeatedCompositeFieldContainer[CustomInlineHeader]
    perf_tracing_file_path: str
    default_regex_engine: _extension_pb2.TypedExtensionConfig
    xds_delegate_extension: _extension_pb2.TypedExtensionConfig
    xds_config_tracker_extension: _extension_pb2.TypedExtensionConfig
    listener_manager: _extension_pb2.TypedExtensionConfig
    application_log_config: Bootstrap.ApplicationLogConfig
    grpc_async_client_manager_config: Bootstrap.GrpcAsyncClientManagerConfig
    memory_allocator_manager: MemoryAllocatorManager
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., node_context_params: _Optional[_Iterable[str]] = ..., static_resources: _Optional[_Union[Bootstrap.StaticResources, _Mapping]] = ..., dynamic_resources: _Optional[_Union[Bootstrap.DynamicResources, _Mapping]] = ..., cluster_manager: _Optional[_Union[ClusterManager, _Mapping]] = ..., hds_config: _Optional[_Union[_config_source_pb2.ApiConfigSource, _Mapping]] = ..., flags_path: _Optional[str] = ..., stats_sinks: _Optional[_Iterable[_Union[_stats_pb2.StatsSink, _Mapping]]] = ..., deferred_stat_options: _Optional[_Union[Bootstrap.DeferredStatOptions, _Mapping]] = ..., stats_config: _Optional[_Union[_stats_pb2.StatsConfig, _Mapping]] = ..., stats_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., stats_flush_on_admin: bool = ..., stats_eviction_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., watchdog: _Optional[_Union[Watchdog, _Mapping]] = ..., watchdogs: _Optional[_Union[Watchdogs, _Mapping]] = ..., tracing: _Optional[_Union[_http_tracer_pb2.Tracing, _Mapping]] = ..., layered_runtime: _Optional[_Union[LayeredRuntime, _Mapping]] = ..., admin: _Optional[_Union[Admin, _Mapping]] = ..., overload_manager: _Optional[_Union[_overload_pb2.OverloadManager, _Mapping]] = ..., enable_dispatcher_stats: bool = ..., header_prefix: _Optional[str] = ..., stats_server_version_override: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., use_tcp_for_dns_lookups: bool = ..., dns_resolution_config: _Optional[_Union[_resolver_pb2.DnsResolutionConfig, _Mapping]] = ..., typed_dns_resolver_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., bootstrap_extensions: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., fatal_actions: _Optional[_Iterable[_Union[FatalAction, _Mapping]]] = ..., config_sources: _Optional[_Iterable[_Union[_config_source_pb2.ConfigSource, _Mapping]]] = ..., default_config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., default_socket_interface: _Optional[str] = ..., certificate_provider_instances: _Optional[_Mapping[str, _extension_pb2.TypedExtensionConfig]] = ..., inline_headers: _Optional[_Iterable[_Union[CustomInlineHeader, _Mapping]]] = ..., perf_tracing_file_path: _Optional[str] = ..., default_regex_engine: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., xds_delegate_extension: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., xds_config_tracker_extension: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., listener_manager: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., application_log_config: _Optional[_Union[Bootstrap.ApplicationLogConfig, _Mapping]] = ..., grpc_async_client_manager_config: _Optional[_Union[Bootstrap.GrpcAsyncClientManagerConfig, _Mapping]] = ..., memory_allocator_manager: _Optional[_Union[MemoryAllocatorManager, _Mapping]] = ...) -> None: ...

class Admin(_message.Message):
    __slots__ = ("access_log", "access_log_path", "profile_path", "address", "socket_options", "ignore_global_conn_limit")
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_PATH_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SOCKET_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    IGNORE_GLOBAL_CONN_LIMIT_FIELD_NUMBER: _ClassVar[int]
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    access_log_path: str
    profile_path: str
    address: _address_pb2.Address
    socket_options: _containers.RepeatedCompositeFieldContainer[_socket_option_pb2.SocketOption]
    ignore_global_conn_limit: bool
    def __init__(self, access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., access_log_path: _Optional[str] = ..., profile_path: _Optional[str] = ..., address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., socket_options: _Optional[_Iterable[_Union[_socket_option_pb2.SocketOption, _Mapping]]] = ..., ignore_global_conn_limit: bool = ...) -> None: ...

class ClusterManager(_message.Message):
    __slots__ = ("local_cluster_name", "outlier_detection", "upstream_bind_config", "load_stats_config", "enable_deferred_cluster_creation")
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
    ENABLE_DEFERRED_CLUSTER_CREATION_FIELD_NUMBER: _ClassVar[int]
    local_cluster_name: str
    outlier_detection: ClusterManager.OutlierDetection
    upstream_bind_config: _address_pb2.BindConfig
    load_stats_config: _config_source_pb2.ApiConfigSource
    enable_deferred_cluster_creation: bool
    def __init__(self, local_cluster_name: _Optional[str] = ..., outlier_detection: _Optional[_Union[ClusterManager.OutlierDetection, _Mapping]] = ..., upstream_bind_config: _Optional[_Union[_address_pb2.BindConfig, _Mapping]] = ..., load_stats_config: _Optional[_Union[_config_source_pb2.ApiConfigSource, _Mapping]] = ..., enable_deferred_cluster_creation: bool = ...) -> None: ...

class Watchdogs(_message.Message):
    __slots__ = ("main_thread_watchdog", "worker_watchdog")
    MAIN_THREAD_WATCHDOG_FIELD_NUMBER: _ClassVar[int]
    WORKER_WATCHDOG_FIELD_NUMBER: _ClassVar[int]
    main_thread_watchdog: Watchdog
    worker_watchdog: Watchdog
    def __init__(self, main_thread_watchdog: _Optional[_Union[Watchdog, _Mapping]] = ..., worker_watchdog: _Optional[_Union[Watchdog, _Mapping]] = ...) -> None: ...

class Watchdog(_message.Message):
    __slots__ = ("actions", "miss_timeout", "megamiss_timeout", "kill_timeout", "max_kill_timeout_jitter", "multikill_timeout", "multikill_threshold")
    class WatchdogAction(_message.Message):
        __slots__ = ("config", "event")
        class WatchdogEvent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN: _ClassVar[Watchdog.WatchdogAction.WatchdogEvent]
            KILL: _ClassVar[Watchdog.WatchdogAction.WatchdogEvent]
            MULTIKILL: _ClassVar[Watchdog.WatchdogAction.WatchdogEvent]
            MEGAMISS: _ClassVar[Watchdog.WatchdogAction.WatchdogEvent]
            MISS: _ClassVar[Watchdog.WatchdogAction.WatchdogEvent]
        UNKNOWN: Watchdog.WatchdogAction.WatchdogEvent
        KILL: Watchdog.WatchdogAction.WatchdogEvent
        MULTIKILL: Watchdog.WatchdogAction.WatchdogEvent
        MEGAMISS: Watchdog.WatchdogAction.WatchdogEvent
        MISS: Watchdog.WatchdogAction.WatchdogEvent
        CONFIG_FIELD_NUMBER: _ClassVar[int]
        EVENT_FIELD_NUMBER: _ClassVar[int]
        config: _extension_pb2.TypedExtensionConfig
        event: Watchdog.WatchdogAction.WatchdogEvent
        def __init__(self, config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., event: _Optional[_Union[Watchdog.WatchdogAction.WatchdogEvent, str]] = ...) -> None: ...
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    MISS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MEGAMISS_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    KILL_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_KILL_TIMEOUT_JITTER_FIELD_NUMBER: _ClassVar[int]
    MULTIKILL_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MULTIKILL_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    actions: _containers.RepeatedCompositeFieldContainer[Watchdog.WatchdogAction]
    miss_timeout: _duration_pb2.Duration
    megamiss_timeout: _duration_pb2.Duration
    kill_timeout: _duration_pb2.Duration
    max_kill_timeout_jitter: _duration_pb2.Duration
    multikill_timeout: _duration_pb2.Duration
    multikill_threshold: _percent_pb2.Percent
    def __init__(self, actions: _Optional[_Iterable[_Union[Watchdog.WatchdogAction, _Mapping]]] = ..., miss_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., megamiss_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., kill_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_kill_timeout_jitter: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., multikill_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., multikill_threshold: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ...) -> None: ...

class FatalAction(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _extension_pb2.TypedExtensionConfig
    def __init__(self, config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...

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

class CustomInlineHeader(_message.Message):
    __slots__ = ("inline_header_name", "inline_header_type")
    class InlineHeaderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REQUEST_HEADER: _ClassVar[CustomInlineHeader.InlineHeaderType]
        REQUEST_TRAILER: _ClassVar[CustomInlineHeader.InlineHeaderType]
        RESPONSE_HEADER: _ClassVar[CustomInlineHeader.InlineHeaderType]
        RESPONSE_TRAILER: _ClassVar[CustomInlineHeader.InlineHeaderType]
    REQUEST_HEADER: CustomInlineHeader.InlineHeaderType
    REQUEST_TRAILER: CustomInlineHeader.InlineHeaderType
    RESPONSE_HEADER: CustomInlineHeader.InlineHeaderType
    RESPONSE_TRAILER: CustomInlineHeader.InlineHeaderType
    INLINE_HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    INLINE_HEADER_TYPE_FIELD_NUMBER: _ClassVar[int]
    inline_header_name: str
    inline_header_type: CustomInlineHeader.InlineHeaderType
    def __init__(self, inline_header_name: _Optional[str] = ..., inline_header_type: _Optional[_Union[CustomInlineHeader.InlineHeaderType, str]] = ...) -> None: ...

class MemoryAllocatorManager(_message.Message):
    __slots__ = ("bytes_to_release", "memory_release_interval")
    BYTES_TO_RELEASE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_RELEASE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    bytes_to_release: int
    memory_release_interval: _duration_pb2.Duration
    def __init__(self, bytes_to_release: _Optional[int] = ..., memory_release_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
