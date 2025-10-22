import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerInfo(_message.Message):
    __slots__ = ("version", "state", "uptime_current_epoch", "uptime_all_epochs", "hot_restart_version", "command_line_options")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LIVE: _ClassVar[ServerInfo.State]
        DRAINING: _ClassVar[ServerInfo.State]
        PRE_INITIALIZING: _ClassVar[ServerInfo.State]
        INITIALIZING: _ClassVar[ServerInfo.State]
    LIVE: ServerInfo.State
    DRAINING: ServerInfo.State
    PRE_INITIALIZING: ServerInfo.State
    INITIALIZING: ServerInfo.State
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    UPTIME_CURRENT_EPOCH_FIELD_NUMBER: _ClassVar[int]
    UPTIME_ALL_EPOCHS_FIELD_NUMBER: _ClassVar[int]
    HOT_RESTART_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMMAND_LINE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    version: str
    state: ServerInfo.State
    uptime_current_epoch: _duration_pb2.Duration
    uptime_all_epochs: _duration_pb2.Duration
    hot_restart_version: str
    command_line_options: CommandLineOptions
    def __init__(self, version: _Optional[str] = ..., state: _Optional[_Union[ServerInfo.State, str]] = ..., uptime_current_epoch: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., uptime_all_epochs: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., hot_restart_version: _Optional[str] = ..., command_line_options: _Optional[_Union[CommandLineOptions, _Mapping]] = ...) -> None: ...

class CommandLineOptions(_message.Message):
    __slots__ = ("base_id", "concurrency", "config_path", "config_yaml", "allow_unknown_static_fields", "reject_unknown_dynamic_fields", "admin_address_path", "local_address_ip_version", "log_level", "component_log_level", "log_format", "log_format_escaped", "log_path", "service_cluster", "service_node", "service_zone", "file_flush_interval", "drain_time", "parent_shutdown_time", "mode", "max_stats", "max_obj_name_len", "disable_hot_restart", "enable_mutex_tracing", "restart_epoch", "cpuset_threads", "disabled_extensions")
    class IpVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        v4: _ClassVar[CommandLineOptions.IpVersion]
        v6: _ClassVar[CommandLineOptions.IpVersion]
    v4: CommandLineOptions.IpVersion
    v6: CommandLineOptions.IpVersion
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Serve: _ClassVar[CommandLineOptions.Mode]
        Validate: _ClassVar[CommandLineOptions.Mode]
        InitOnly: _ClassVar[CommandLineOptions.Mode]
    Serve: CommandLineOptions.Mode
    Validate: CommandLineOptions.Mode
    InitOnly: CommandLineOptions.Mode
    BASE_ID_FIELD_NUMBER: _ClassVar[int]
    CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
    CONFIG_PATH_FIELD_NUMBER: _ClassVar[int]
    CONFIG_YAML_FIELD_NUMBER: _ClassVar[int]
    ALLOW_UNKNOWN_STATIC_FIELDS_FIELD_NUMBER: _ClassVar[int]
    REJECT_UNKNOWN_DYNAMIC_FIELDS_FIELD_NUMBER: _ClassVar[int]
    ADMIN_ADDRESS_PATH_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ADDRESS_IP_VERSION_FIELD_NUMBER: _ClassVar[int]
    LOG_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_LOG_LEVEL_FIELD_NUMBER: _ClassVar[int]
    LOG_FORMAT_FIELD_NUMBER: _ClassVar[int]
    LOG_FORMAT_ESCAPED_FIELD_NUMBER: _ClassVar[int]
    LOG_PATH_FIELD_NUMBER: _ClassVar[int]
    SERVICE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NODE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ZONE_FIELD_NUMBER: _ClassVar[int]
    FILE_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    DRAIN_TIME_FIELD_NUMBER: _ClassVar[int]
    PARENT_SHUTDOWN_TIME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    MAX_STATS_FIELD_NUMBER: _ClassVar[int]
    MAX_OBJ_NAME_LEN_FIELD_NUMBER: _ClassVar[int]
    DISABLE_HOT_RESTART_FIELD_NUMBER: _ClassVar[int]
    ENABLE_MUTEX_TRACING_FIELD_NUMBER: _ClassVar[int]
    RESTART_EPOCH_FIELD_NUMBER: _ClassVar[int]
    CPUSET_THREADS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    base_id: int
    concurrency: int
    config_path: str
    config_yaml: str
    allow_unknown_static_fields: bool
    reject_unknown_dynamic_fields: bool
    admin_address_path: str
    local_address_ip_version: CommandLineOptions.IpVersion
    log_level: str
    component_log_level: str
    log_format: str
    log_format_escaped: bool
    log_path: str
    service_cluster: str
    service_node: str
    service_zone: str
    file_flush_interval: _duration_pb2.Duration
    drain_time: _duration_pb2.Duration
    parent_shutdown_time: _duration_pb2.Duration
    mode: CommandLineOptions.Mode
    max_stats: int
    max_obj_name_len: int
    disable_hot_restart: bool
    enable_mutex_tracing: bool
    restart_epoch: int
    cpuset_threads: bool
    disabled_extensions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, base_id: _Optional[int] = ..., concurrency: _Optional[int] = ..., config_path: _Optional[str] = ..., config_yaml: _Optional[str] = ..., allow_unknown_static_fields: bool = ..., reject_unknown_dynamic_fields: bool = ..., admin_address_path: _Optional[str] = ..., local_address_ip_version: _Optional[_Union[CommandLineOptions.IpVersion, str]] = ..., log_level: _Optional[str] = ..., component_log_level: _Optional[str] = ..., log_format: _Optional[str] = ..., log_format_escaped: bool = ..., log_path: _Optional[str] = ..., service_cluster: _Optional[str] = ..., service_node: _Optional[str] = ..., service_zone: _Optional[str] = ..., file_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., drain_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., parent_shutdown_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., mode: _Optional[_Union[CommandLineOptions.Mode, str]] = ..., max_stats: _Optional[int] = ..., max_obj_name_len: _Optional[int] = ..., disable_hot_restart: bool = ..., enable_mutex_tracing: bool = ..., restart_epoch: _Optional[int] = ..., cpuset_threads: bool = ..., disabled_extensions: _Optional[_Iterable[str]] = ...) -> None: ...
