import datetime

from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.config.filter.accesslog.v2 import accesslog_pb2 as _accesslog_pb2
from envoy.type import hash_policy_pb2 as _hash_policy_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TcpProxy(_message.Message):
    __slots__ = ("stat_prefix", "cluster", "weighted_clusters", "metadata_match", "idle_timeout", "downstream_idle_timeout", "upstream_idle_timeout", "access_log", "deprecated_v1", "max_connect_attempts", "hash_policy", "tunneling_config")
    class DeprecatedV1(_message.Message):
        __slots__ = ("routes",)
        class TCPRoute(_message.Message):
            __slots__ = ("cluster", "destination_ip_list", "destination_ports", "source_ip_list", "source_ports")
            CLUSTER_FIELD_NUMBER: _ClassVar[int]
            DESTINATION_IP_LIST_FIELD_NUMBER: _ClassVar[int]
            DESTINATION_PORTS_FIELD_NUMBER: _ClassVar[int]
            SOURCE_IP_LIST_FIELD_NUMBER: _ClassVar[int]
            SOURCE_PORTS_FIELD_NUMBER: _ClassVar[int]
            cluster: str
            destination_ip_list: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
            destination_ports: str
            source_ip_list: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
            source_ports: str
            def __init__(self, cluster: _Optional[str] = ..., destination_ip_list: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., destination_ports: _Optional[str] = ..., source_ip_list: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., source_ports: _Optional[str] = ...) -> None: ...
        ROUTES_FIELD_NUMBER: _ClassVar[int]
        routes: _containers.RepeatedCompositeFieldContainer[TcpProxy.DeprecatedV1.TCPRoute]
        def __init__(self, routes: _Optional[_Iterable[_Union[TcpProxy.DeprecatedV1.TCPRoute, _Mapping]]] = ...) -> None: ...
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
        __slots__ = ("hostname",)
        HOSTNAME_FIELD_NUMBER: _ClassVar[int]
        hostname: str
        def __init__(self, hostname: _Optional[str] = ...) -> None: ...
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    WEIGHTED_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_V1_FIELD_NUMBER: _ClassVar[int]
    MAX_CONNECT_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    HASH_POLICY_FIELD_NUMBER: _ClassVar[int]
    TUNNELING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    cluster: str
    weighted_clusters: TcpProxy.WeightedCluster
    metadata_match: _base_pb2.Metadata
    idle_timeout: _duration_pb2.Duration
    downstream_idle_timeout: _duration_pb2.Duration
    upstream_idle_timeout: _duration_pb2.Duration
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    deprecated_v1: TcpProxy.DeprecatedV1
    max_connect_attempts: _wrappers_pb2.UInt32Value
    hash_policy: _containers.RepeatedCompositeFieldContainer[_hash_policy_pb2.HashPolicy]
    tunneling_config: TcpProxy.TunnelingConfig
    def __init__(self, stat_prefix: _Optional[str] = ..., cluster: _Optional[str] = ..., weighted_clusters: _Optional[_Union[TcpProxy.WeightedCluster, _Mapping]] = ..., metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., downstream_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upstream_idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., deprecated_v1: _Optional[_Union[TcpProxy.DeprecatedV1, _Mapping]] = ..., max_connect_attempts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., hash_policy: _Optional[_Iterable[_Union[_hash_policy_pb2.HashPolicy, _Mapping]]] = ..., tunneling_config: _Optional[_Union[TcpProxy.TunnelingConfig, _Mapping]] = ...) -> None: ...
