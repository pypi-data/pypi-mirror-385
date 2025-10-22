from envoy.config.cluster.v3 import cluster_pb2 as _cluster_pb2
from envoy.type.metadata.v3 import metadata_pb2 as _metadata_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OverrideHost(_message.Message):
    __slots__ = ("override_host_sources", "fallback_policy")
    class OverrideHostSource(_message.Message):
        __slots__ = ("header", "metadata")
        HEADER_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        header: str
        metadata: _metadata_pb2.MetadataKey
        def __init__(self, header: _Optional[str] = ..., metadata: _Optional[_Union[_metadata_pb2.MetadataKey, _Mapping]] = ...) -> None: ...
    OVERRIDE_HOST_SOURCES_FIELD_NUMBER: _ClassVar[int]
    FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
    override_host_sources: _containers.RepeatedCompositeFieldContainer[OverrideHost.OverrideHostSource]
    fallback_policy: _cluster_pb2.LoadBalancingPolicy
    def __init__(self, override_host_sources: _Optional[_Iterable[_Union[OverrideHost.OverrideHostSource, _Mapping]]] = ..., fallback_policy: _Optional[_Union[_cluster_pb2.LoadBalancingPolicy, _Mapping]] = ...) -> None: ...
