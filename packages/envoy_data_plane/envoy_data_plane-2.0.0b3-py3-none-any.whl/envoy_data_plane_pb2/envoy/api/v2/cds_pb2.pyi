from envoy.api.v2 import discovery_pb2 as _discovery_pb2
from google.api import annotations_pb2 as _annotations_pb2
from envoy.annotations import resource_pb2 as _resource_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from envoy.api.v2 import cluster_pb2 as _cluster_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar
from envoy.api.v2.cluster_pb2 import Cluster as Cluster
from envoy.api.v2.cluster_pb2 import LoadBalancingPolicy as LoadBalancingPolicy
from envoy.api.v2.cluster_pb2 import UpstreamBindConfig as UpstreamBindConfig
from envoy.api.v2.cluster_pb2 import UpstreamConnectionOptions as UpstreamConnectionOptions

DESCRIPTOR: _descriptor.FileDescriptor

class CdsDummy(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
