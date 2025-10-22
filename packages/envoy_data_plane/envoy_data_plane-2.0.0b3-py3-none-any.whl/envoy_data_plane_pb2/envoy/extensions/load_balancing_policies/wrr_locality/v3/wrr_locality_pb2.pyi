from envoy.config.cluster.v3 import cluster_pb2 as _cluster_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WrrLocality(_message.Message):
    __slots__ = ("endpoint_picking_policy",)
    ENDPOINT_PICKING_POLICY_FIELD_NUMBER: _ClassVar[int]
    endpoint_picking_policy: _cluster_pb2.LoadBalancingPolicy
    def __init__(self, endpoint_picking_policy: _Optional[_Union[_cluster_pb2.LoadBalancingPolicy, _Mapping]] = ...) -> None: ...
