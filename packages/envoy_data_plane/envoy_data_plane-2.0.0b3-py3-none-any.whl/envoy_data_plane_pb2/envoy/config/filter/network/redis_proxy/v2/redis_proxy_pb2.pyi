import datetime

from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RedisProxy(_message.Message):
    __slots__ = ("stat_prefix", "cluster", "settings", "latency_in_micros", "prefix_routes", "downstream_auth_password")
    class ConnPoolSettings(_message.Message):
        __slots__ = ("op_timeout", "enable_hashtagging", "enable_redirection", "max_buffer_size_before_flush", "buffer_flush_timeout", "max_upstream_unknown_connections", "enable_command_stats", "read_policy")
        class ReadPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MASTER: _ClassVar[RedisProxy.ConnPoolSettings.ReadPolicy]
            PREFER_MASTER: _ClassVar[RedisProxy.ConnPoolSettings.ReadPolicy]
            REPLICA: _ClassVar[RedisProxy.ConnPoolSettings.ReadPolicy]
            PREFER_REPLICA: _ClassVar[RedisProxy.ConnPoolSettings.ReadPolicy]
            ANY: _ClassVar[RedisProxy.ConnPoolSettings.ReadPolicy]
        MASTER: RedisProxy.ConnPoolSettings.ReadPolicy
        PREFER_MASTER: RedisProxy.ConnPoolSettings.ReadPolicy
        REPLICA: RedisProxy.ConnPoolSettings.ReadPolicy
        PREFER_REPLICA: RedisProxy.ConnPoolSettings.ReadPolicy
        ANY: RedisProxy.ConnPoolSettings.ReadPolicy
        OP_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        ENABLE_HASHTAGGING_FIELD_NUMBER: _ClassVar[int]
        ENABLE_REDIRECTION_FIELD_NUMBER: _ClassVar[int]
        MAX_BUFFER_SIZE_BEFORE_FLUSH_FIELD_NUMBER: _ClassVar[int]
        BUFFER_FLUSH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        MAX_UPSTREAM_UNKNOWN_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
        ENABLE_COMMAND_STATS_FIELD_NUMBER: _ClassVar[int]
        READ_POLICY_FIELD_NUMBER: _ClassVar[int]
        op_timeout: _duration_pb2.Duration
        enable_hashtagging: bool
        enable_redirection: bool
        max_buffer_size_before_flush: int
        buffer_flush_timeout: _duration_pb2.Duration
        max_upstream_unknown_connections: _wrappers_pb2.UInt32Value
        enable_command_stats: bool
        read_policy: RedisProxy.ConnPoolSettings.ReadPolicy
        def __init__(self, op_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., enable_hashtagging: bool = ..., enable_redirection: bool = ..., max_buffer_size_before_flush: _Optional[int] = ..., buffer_flush_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_upstream_unknown_connections: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enable_command_stats: bool = ..., read_policy: _Optional[_Union[RedisProxy.ConnPoolSettings.ReadPolicy, str]] = ...) -> None: ...
    class PrefixRoutes(_message.Message):
        __slots__ = ("routes", "case_insensitive", "catch_all_cluster", "catch_all_route")
        class Route(_message.Message):
            __slots__ = ("prefix", "remove_prefix", "cluster", "request_mirror_policy")
            class RequestMirrorPolicy(_message.Message):
                __slots__ = ("cluster", "runtime_fraction", "exclude_read_commands")
                CLUSTER_FIELD_NUMBER: _ClassVar[int]
                RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
                EXCLUDE_READ_COMMANDS_FIELD_NUMBER: _ClassVar[int]
                cluster: str
                runtime_fraction: _base_pb2.RuntimeFractionalPercent
                exclude_read_commands: bool
                def __init__(self, cluster: _Optional[str] = ..., runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., exclude_read_commands: bool = ...) -> None: ...
            PREFIX_FIELD_NUMBER: _ClassVar[int]
            REMOVE_PREFIX_FIELD_NUMBER: _ClassVar[int]
            CLUSTER_FIELD_NUMBER: _ClassVar[int]
            REQUEST_MIRROR_POLICY_FIELD_NUMBER: _ClassVar[int]
            prefix: str
            remove_prefix: bool
            cluster: str
            request_mirror_policy: _containers.RepeatedCompositeFieldContainer[RedisProxy.PrefixRoutes.Route.RequestMirrorPolicy]
            def __init__(self, prefix: _Optional[str] = ..., remove_prefix: bool = ..., cluster: _Optional[str] = ..., request_mirror_policy: _Optional[_Iterable[_Union[RedisProxy.PrefixRoutes.Route.RequestMirrorPolicy, _Mapping]]] = ...) -> None: ...
        ROUTES_FIELD_NUMBER: _ClassVar[int]
        CASE_INSENSITIVE_FIELD_NUMBER: _ClassVar[int]
        CATCH_ALL_CLUSTER_FIELD_NUMBER: _ClassVar[int]
        CATCH_ALL_ROUTE_FIELD_NUMBER: _ClassVar[int]
        routes: _containers.RepeatedCompositeFieldContainer[RedisProxy.PrefixRoutes.Route]
        case_insensitive: bool
        catch_all_cluster: str
        catch_all_route: RedisProxy.PrefixRoutes.Route
        def __init__(self, routes: _Optional[_Iterable[_Union[RedisProxy.PrefixRoutes.Route, _Mapping]]] = ..., case_insensitive: bool = ..., catch_all_cluster: _Optional[str] = ..., catch_all_route: _Optional[_Union[RedisProxy.PrefixRoutes.Route, _Mapping]] = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    LATENCY_IN_MICROS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_ROUTES_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    cluster: str
    settings: RedisProxy.ConnPoolSettings
    latency_in_micros: bool
    prefix_routes: RedisProxy.PrefixRoutes
    downstream_auth_password: _base_pb2.DataSource
    def __init__(self, stat_prefix: _Optional[str] = ..., cluster: _Optional[str] = ..., settings: _Optional[_Union[RedisProxy.ConnPoolSettings, _Mapping]] = ..., latency_in_micros: bool = ..., prefix_routes: _Optional[_Union[RedisProxy.PrefixRoutes, _Mapping]] = ..., downstream_auth_password: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...

class RedisProtocolOptions(_message.Message):
    __slots__ = ("auth_password",)
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    auth_password: _base_pb2.DataSource
    def __init__(self, auth_password: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
