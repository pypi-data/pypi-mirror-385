import datetime

from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.core.v3 import backoff_pb2 as _backoff_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import proxy_protocol_pb2 as _proxy_protocol_pb2
from envoy.extensions.filters.network.http_connection_manager.v3 import http_connection_manager_pb2 as _http_connection_manager_pb2
from envoy.type.v3 import hash_policy_pb2 as _hash_policy_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TcpProxy(_message.Message):
    __slots__ = ("stat_prefix", "cluster", "weighted_clusters", "on_demand", "metadata_match", "idle_timeout", "downstream_idle_timeout", "upstream_idle_timeout", "access_log", "max_connect_attempts", "backoff_options", "hash_policy", "tunneling_config", "max_downstream_connection_duration", "max_downstream_connection_duration_jitter_percentage", "access_log_flush_interval", "flush_access_log_on_connected", "access_log_options", "proxy_protocol_tlvs")
    class WeightedCluster(_message.Message):
        __slots__ = ("clusters",)
        class ClusterWeight(_message.Message):
            __slots__ = ("name", "weight", "metadata_match")
            NAME_FIELD_NUMBER: _ClassVar[int]
            WEIGHT_FIELD_NUMBER: _ClassVar[int]
            METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
            name: str
            weight: int
            metadata_match: _base_pb2.Metadata
            def __init__(self, name: _Optional[str] = ..., weight: _Optional[int] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...
        CLUSTERS_FIELD_NUMBER: _ClassVar[int]
        clusters: _containers.RepeatedCompositeFieldContainer[TcpProxy.WeightedCluster.ClusterWeight]
        def __init__(self, clusters: _Optional[_Iterable[_Union[TcpProxy.WeightedCluster.ClusterWeight, _Mapping]]] = ...) -> None: ...
    class TunnelingConfig(_message.Message):
        __slots__ = ("hostname", "use_post", "headers_to_add", "propagate_response_headers", "post_path", "propagate_response_trailers", "request_id_extension", "request_id_header", "request_id_metadata_key")
        HOSTNAME_FIELD_NUMBER: _ClassVar[int]
        USE_POST_FIELD_NUMBER: _ClassVar[int]
        HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
        PROPAGATE_RESPONSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
        POST_PATH_FIELD_NUMBER: _ClassVar[int]
        PROPAGATE_RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
        REQUEST_ID_EXTENSION_FIELD_NUMBER: _ClassVar[int]
        REQUEST_ID_HEADER_FIELD_NUMBER: _ClassVar[int]
        REQUEST_ID_METADATA_KEY_FIELD_NUMBER: _ClassVar[int]
        hostname: str
        use_post: bool
        headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
        propagate_response_headers: bool
        post_path: str
        propagate_response_trailers: bool
        request_id_extension: _http_connection_manager_pb2.RequestIDExtension
        request_id_header: str
        request_id_metadata_key: str
        def __init__(self, hostname: _Optional[str] = ..., use_post: bool = ..., headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., propagate_response_headers: bool = ..., post_path: _Optional[str] = ..., propagate_response_trailers: bool = ..., request_id_extension: _Optional[_Union[_http_connection_manager_pb2.RequestIDExtension, _Mapping]] = ..., request_id_header: _Optional[str] = ..., request_id_metadata_key: _Optional[str] = ...) -> None: ...
    class OnDemand(_message.Message):
        __slots__ = ("odcds_config", "resources_locator", "timeout")
        ODCDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        RESOURCES_LOCATOR_FIELD_NUMBER: _ClassVar[int]
        TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        odcds_config: _config_source_pb2.ConfigSource
        resources_locator: str
        timeout: _duration_pb2.Duration
        def __init__(self, odcds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., resources_locator: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class TcpAccessLogOptions(_message.Message):
        __slots__ = ("access_log_flush_interval", "flush_access_log_on_connected")
        ACCESS_LOG_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        FLUSH_ACCESS_LOG_ON_CONNECTED_FIELD_NUMBER: _ClassVar[int]
        access_log_flush_interval: _duration_pb2.Duration
        flush_access_log_on_connected: bool
        def __init__(self, access_log_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., flush_access_log_on_connected: bool = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    ON_DEMAND_FIELD_NUMBER: _ClassVar[int]
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    MAX_CONNECT_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    BACKOFF_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HASH_POLICY_FIELD_NUMBER: _ClassVar[int]
    TUNNELING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    MAX_DOWNSTREAM_CONNECTION_DURATION_FIELD_NUMBER: _ClassVar[int]
    MAX_DOWNSTREAM_CONNECTION_DURATION_JITTER_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    FLUSH_ACCESS_LOG_ON_CONNECTED_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    PROXY_PROTOCOL_TLVS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    cluster: str
    weighted_clusters: TcpProxy.WeightedCluster
    on_demand: TcpProxy.OnDemand
    metadata_match: _base_pb2.Metadata
    idle_timeout: _duration_pb2.Duration
    downstream_idle_timeout: _duration_pb2.Duration
    upstream_idle_timeout: _duration_pb2.Duration
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    max_connect_attempts: _wrappers_pb2.UInt32Value
    backoff_options: _backoff_pb2.BackoffStrategy
    hash_policy: _containers.RepeatedCompositeFieldContainer[_hash_policy_pb2.HashPolicy]
    tunneling_config: TcpProxy.TunnelingConfig
    max_downstream_connection_duration: _duration_pb2.Duration
    max_downstream_connection_duration_jitter_percentage: _percent_pb2.Percent
    access_log_flush_interval: _duration_pb2.Duration
    flush_access_log_on_connected: bool
    access_log_options: TcpProxy.TcpAccessLogOptions
    proxy_protocol_tlvs: _containers.RepeatedCompositeFieldContainer[_proxy_protocol_pb2.TlvEntry]
    def __init__(self, stat_prefix: _Optional[str] = ..., cluster: _Optional[str] = ..., weighted_clusters: _Optional[_Union[TcpProxy.WeightedCluster, _Mapping]] = ..., on_demand: _Optional[_Union[TcpProxy.OnDemand, _Mapping]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., downstream_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upstream_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., max_connect_attempts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., backoff_options: _Optional[_Union[_backoff_pb2.BackoffStrategy, _Mapping]] = ..., hash_policy: _Optional[_Iterable[_Union[_hash_policy_pb2.HashPolicy, _Mapping]]] = ..., tunneling_config: _Optional[_Union[TcpProxy.TunnelingConfig, _Mapping]] = ..., max_downstream_connection_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_downstream_connection_duration_jitter_percentage: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., access_log_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., flush_access_log_on_connected: bool = ..., access_log_options: _Optional[_Union[TcpProxy.TcpAccessLogOptions, _Mapping]] = ..., proxy_protocol_tlvs: _Optional[_Iterable[_Union[_proxy_protocol_pb2.TlvEntry, _Mapping]]] = ...) -> None: ...
