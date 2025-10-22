import datetime

from envoy.config.cluster.v3 import cluster_pb2 as _cluster_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.extensions.common.dynamic_forward_proxy.v3 import dns_cache_pb2 as _dns_cache_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClusterConfig(_message.Message):
    __slots__ = ("dns_cache_config", "sub_clusters_config", "allow_insecure_cluster_options", "allow_coalesced_connections")
    DNS_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SUB_CLUSTERS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ALLOW_INSECURE_CLUSTER_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_COALESCED_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    dns_cache_config: _dns_cache_pb2.DnsCacheConfig
    sub_clusters_config: SubClustersConfig
    allow_insecure_cluster_options: bool
    allow_coalesced_connections: bool
    def __init__(self, dns_cache_config: _Optional[_Union[_dns_cache_pb2.DnsCacheConfig, _Mapping]] = ..., sub_clusters_config: _Optional[_Union[SubClustersConfig, _Mapping]] = ..., allow_insecure_cluster_options: bool = ..., allow_coalesced_connections: bool = ...) -> None: ...

class SubClustersConfig(_message.Message):
    __slots__ = ("lb_policy", "max_sub_clusters", "sub_cluster_ttl", "preresolve_clusters")
    LB_POLICY_FIELD_NUMBER: _ClassVar[int]
    MAX_SUB_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    SUB_CLUSTER_TTL_FIELD_NUMBER: _ClassVar[int]
    PRERESOLVE_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    lb_policy: _cluster_pb2.Cluster.LbPolicy
    max_sub_clusters: _wrappers_pb2.UInt32Value
    sub_cluster_ttl: _duration_pb2.Duration
    preresolve_clusters: _containers.RepeatedCompositeFieldContainer[_address_pb2.SocketAddress]
    def __init__(self, lb_policy: _Optional[_Union[_cluster_pb2.Cluster.LbPolicy, str]] = ..., max_sub_clusters: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., sub_cluster_ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., preresolve_clusters: _Optional[_Iterable[_Union[_address_pb2.SocketAddress, _Mapping]]] = ...) -> None: ...
