import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.extensions.common.aws.v3 import credential_provider_pb2 as _credential_provider_pb2
from envoy.extensions.common.dynamic_forward_proxy.v3 import dns_cache_pb2 as _dns_cache_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
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

class RedisProxy(_message.Message):
    __slots__ = ("stat_prefix", "settings", "latency_in_micros", "prefix_routes", "downstream_auth_password", "downstream_auth_passwords", "faults", "downstream_auth_username", "external_auth_provider", "custom_commands")
    class ConnPoolSettings(_message.Message):
        __slots__ = ("op_timeout", "enable_hashtagging", "enable_redirection", "dns_cache_config", "max_buffer_size_before_flush", "buffer_flush_timeout", "max_upstream_unknown_connections", "enable_command_stats", "read_policy", "connection_rate_limit")
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
        DNS_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
        MAX_BUFFER_SIZE_BEFORE_FLUSH_FIELD_NUMBER: _ClassVar[int]
        BUFFER_FLUSH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        MAX_UPSTREAM_UNKNOWN_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
        ENABLE_COMMAND_STATS_FIELD_NUMBER: _ClassVar[int]
        READ_POLICY_FIELD_NUMBER: _ClassVar[int]
        CONNECTION_RATE_LIMIT_FIELD_NUMBER: _ClassVar[int]
        op_timeout: _duration_pb2.Duration
        enable_hashtagging: bool
        enable_redirection: bool
        dns_cache_config: _dns_cache_pb2.DnsCacheConfig
        max_buffer_size_before_flush: int
        buffer_flush_timeout: _duration_pb2.Duration
        max_upstream_unknown_connections: _wrappers_pb2.UInt32Value
        enable_command_stats: bool
        read_policy: RedisProxy.ConnPoolSettings.ReadPolicy
        connection_rate_limit: RedisProxy.ConnectionRateLimit
        def __init__(self, op_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., enable_hashtagging: bool = ..., enable_redirection: bool = ..., dns_cache_config: _Optional[_Union[_dns_cache_pb2.DnsCacheConfig, _Mapping]] = ..., max_buffer_size_before_flush: _Optional[int] = ..., buffer_flush_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_upstream_unknown_connections: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enable_command_stats: bool = ..., read_policy: _Optional[_Union[RedisProxy.ConnPoolSettings.ReadPolicy, str]] = ..., connection_rate_limit: _Optional[_Union[RedisProxy.ConnectionRateLimit, _Mapping]] = ...) -> None: ...
    class PrefixRoutes(_message.Message):
        __slots__ = ("routes", "case_insensitive", "catch_all_route")
        class Route(_message.Message):
            __slots__ = ("prefix", "remove_prefix", "cluster", "request_mirror_policy", "key_formatter", "read_command_policy")
            class RequestMirrorPolicy(_message.Message):
                __slots__ = ("cluster", "runtime_fraction", "exclude_read_commands")
                CLUSTER_FIELD_NUMBER: _ClassVar[int]
                RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
                EXCLUDE_READ_COMMANDS_FIELD_NUMBER: _ClassVar[int]
                cluster: str
                runtime_fraction: _base_pb2.RuntimeFractionalPercent
                exclude_read_commands: bool
                def __init__(self, cluster: _Optional[str] = ..., runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., exclude_read_commands: bool = ...) -> None: ...
            class ReadCommandPolicy(_message.Message):
                __slots__ = ("cluster",)
                CLUSTER_FIELD_NUMBER: _ClassVar[int]
                cluster: str
                def __init__(self, cluster: _Optional[str] = ...) -> None: ...
            PREFIX_FIELD_NUMBER: _ClassVar[int]
            REMOVE_PREFIX_FIELD_NUMBER: _ClassVar[int]
            CLUSTER_FIELD_NUMBER: _ClassVar[int]
            REQUEST_MIRROR_POLICY_FIELD_NUMBER: _ClassVar[int]
            KEY_FORMATTER_FIELD_NUMBER: _ClassVar[int]
            READ_COMMAND_POLICY_FIELD_NUMBER: _ClassVar[int]
            prefix: str
            remove_prefix: bool
            cluster: str
            request_mirror_policy: _containers.RepeatedCompositeFieldContainer[RedisProxy.PrefixRoutes.Route.RequestMirrorPolicy]
            key_formatter: str
            read_command_policy: RedisProxy.PrefixRoutes.Route.ReadCommandPolicy
            def __init__(self, prefix: _Optional[str] = ..., remove_prefix: bool = ..., cluster: _Optional[str] = ..., request_mirror_policy: _Optional[_Iterable[_Union[RedisProxy.PrefixRoutes.Route.RequestMirrorPolicy, _Mapping]]] = ..., key_formatter: _Optional[str] = ..., read_command_policy: _Optional[_Union[RedisProxy.PrefixRoutes.Route.ReadCommandPolicy, _Mapping]] = ...) -> None: ...
        ROUTES_FIELD_NUMBER: _ClassVar[int]
        CASE_INSENSITIVE_FIELD_NUMBER: _ClassVar[int]
        CATCH_ALL_ROUTE_FIELD_NUMBER: _ClassVar[int]
        routes: _containers.RepeatedCompositeFieldContainer[RedisProxy.PrefixRoutes.Route]
        case_insensitive: bool
        catch_all_route: RedisProxy.PrefixRoutes.Route
        def __init__(self, routes: _Optional[_Iterable[_Union[RedisProxy.PrefixRoutes.Route, _Mapping]]] = ..., case_insensitive: bool = ..., catch_all_route: _Optional[_Union[RedisProxy.PrefixRoutes.Route, _Mapping]] = ...) -> None: ...
    class RedisFault(_message.Message):
        __slots__ = ("fault_type", "fault_enabled", "delay", "commands")
        class RedisFaultType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DELAY: _ClassVar[RedisProxy.RedisFault.RedisFaultType]
            ERROR: _ClassVar[RedisProxy.RedisFault.RedisFaultType]
        DELAY: RedisProxy.RedisFault.RedisFaultType
        ERROR: RedisProxy.RedisFault.RedisFaultType
        FAULT_TYPE_FIELD_NUMBER: _ClassVar[int]
        FAULT_ENABLED_FIELD_NUMBER: _ClassVar[int]
        DELAY_FIELD_NUMBER: _ClassVar[int]
        COMMANDS_FIELD_NUMBER: _ClassVar[int]
        fault_type: RedisProxy.RedisFault.RedisFaultType
        fault_enabled: _base_pb2.RuntimeFractionalPercent
        delay: _duration_pb2.Duration
        commands: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, fault_type: _Optional[_Union[RedisProxy.RedisFault.RedisFaultType, str]] = ..., fault_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., delay: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., commands: _Optional[_Iterable[str]] = ...) -> None: ...
    class ConnectionRateLimit(_message.Message):
        __slots__ = ("connection_rate_limit_per_sec",)
        CONNECTION_RATE_LIMIT_PER_SEC_FIELD_NUMBER: _ClassVar[int]
        connection_rate_limit_per_sec: int
        def __init__(self, connection_rate_limit_per_sec: _Optional[int] = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    LATENCY_IN_MICROS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_ROUTES_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_AUTH_PASSWORDS_FIELD_NUMBER: _ClassVar[int]
    FAULTS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_AUTH_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_COMMANDS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    settings: RedisProxy.ConnPoolSettings
    latency_in_micros: bool
    prefix_routes: RedisProxy.PrefixRoutes
    downstream_auth_password: _base_pb2.DataSource
    downstream_auth_passwords: _containers.RepeatedCompositeFieldContainer[_base_pb2.DataSource]
    faults: _containers.RepeatedCompositeFieldContainer[RedisProxy.RedisFault]
    downstream_auth_username: _base_pb2.DataSource
    external_auth_provider: RedisExternalAuthProvider
    custom_commands: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, stat_prefix: _Optional[str] = ..., settings: _Optional[_Union[RedisProxy.ConnPoolSettings, _Mapping]] = ..., latency_in_micros: bool = ..., prefix_routes: _Optional[_Union[RedisProxy.PrefixRoutes, _Mapping]] = ..., downstream_auth_password: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., downstream_auth_passwords: _Optional[_Iterable[_Union[_base_pb2.DataSource, _Mapping]]] = ..., faults: _Optional[_Iterable[_Union[RedisProxy.RedisFault, _Mapping]]] = ..., downstream_auth_username: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., external_auth_provider: _Optional[_Union[RedisExternalAuthProvider, _Mapping]] = ..., custom_commands: _Optional[_Iterable[str]] = ...) -> None: ...

class RedisProtocolOptions(_message.Message):
    __slots__ = ("auth_password", "auth_username", "aws_iam")
    AUTH_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    AUTH_USERNAME_FIELD_NUMBER: _ClassVar[int]
    AWS_IAM_FIELD_NUMBER: _ClassVar[int]
    auth_password: _base_pb2.DataSource
    auth_username: _base_pb2.DataSource
    aws_iam: AwsIam
    def __init__(self, auth_password: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., auth_username: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., aws_iam: _Optional[_Union[AwsIam, _Mapping]] = ...) -> None: ...

class AwsIam(_message.Message):
    __slots__ = ("credential_provider", "cache_name", "service_name", "region", "expiration_time")
    CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CACHE_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_TIME_FIELD_NUMBER: _ClassVar[int]
    credential_provider: _credential_provider_pb2.AwsCredentialProvider
    cache_name: str
    service_name: str
    region: str
    expiration_time: _duration_pb2.Duration
    def __init__(self, credential_provider: _Optional[_Union[_credential_provider_pb2.AwsCredentialProvider, _Mapping]] = ..., cache_name: _Optional[str] = ..., service_name: _Optional[str] = ..., region: _Optional[str] = ..., expiration_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class RedisExternalAuthProvider(_message.Message):
    __slots__ = ("grpc_service", "enable_auth_expiration")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_AUTH_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    enable_auth_expiration: bool
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., enable_auth_expiration: bool = ...) -> None: ...
