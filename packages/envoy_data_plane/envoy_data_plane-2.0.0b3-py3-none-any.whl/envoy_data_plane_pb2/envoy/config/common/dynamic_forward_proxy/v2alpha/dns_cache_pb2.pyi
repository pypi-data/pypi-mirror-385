import datetime

from envoy.api.v2 import cluster_pb2 as _cluster_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DnsCacheConfig(_message.Message):
    __slots__ = ("name", "dns_lookup_family", "dns_refresh_rate", "host_ttl", "max_hosts", "dns_failure_refresh_rate")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DNS_LOOKUP_FAMILY_FIELD_NUMBER: _ClassVar[int]
    DNS_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    HOST_TTL_FIELD_NUMBER: _ClassVar[int]
    MAX_HOSTS_FIELD_NUMBER: _ClassVar[int]
    DNS_FAILURE_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    dns_lookup_family: _cluster_pb2.Cluster.DnsLookupFamily
    dns_refresh_rate: _duration_pb2.Duration
    host_ttl: _duration_pb2.Duration
    max_hosts: _wrappers_pb2.UInt32Value
    dns_failure_refresh_rate: _cluster_pb2.Cluster.RefreshRate
    def __init__(self, name: _Optional[str] = ..., dns_lookup_family: _Optional[_Union[_cluster_pb2.Cluster.DnsLookupFamily, str]] = ..., dns_refresh_rate: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., host_ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_hosts: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., dns_failure_refresh_rate: _Optional[_Union[_cluster_pb2.Cluster.RefreshRate, _Mapping]] = ...) -> None: ...
