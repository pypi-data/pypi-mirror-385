from envoy.admin.v2alpha import config_dump_pb2 as _config_dump_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.type.matcher import node_pb2 as _node_pb2
from google.api import annotations_pb2 as _annotations_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[ConfigStatus]
    SYNCED: _ClassVar[ConfigStatus]
    NOT_SENT: _ClassVar[ConfigStatus]
    STALE: _ClassVar[ConfigStatus]
    ERROR: _ClassVar[ConfigStatus]
UNKNOWN: ConfigStatus
SYNCED: ConfigStatus
NOT_SENT: ConfigStatus
STALE: ConfigStatus
ERROR: ConfigStatus

class ClientStatusRequest(_message.Message):
    __slots__ = ("node_matchers",)
    NODE_MATCHERS_FIELD_NUMBER: _ClassVar[int]
    node_matchers: _containers.RepeatedCompositeFieldContainer[_node_pb2.NodeMatcher]
    def __init__(self, node_matchers: _Optional[_Iterable[_Union[_node_pb2.NodeMatcher, _Mapping]]] = ...) -> None: ...

class PerXdsConfig(_message.Message):
    __slots__ = ("status", "listener_config", "cluster_config", "route_config", "scoped_route_config")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LISTENER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCOPED_ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    status: ConfigStatus
    listener_config: _config_dump_pb2.ListenersConfigDump
    cluster_config: _config_dump_pb2.ClustersConfigDump
    route_config: _config_dump_pb2.RoutesConfigDump
    scoped_route_config: _config_dump_pb2.ScopedRoutesConfigDump
    def __init__(self, status: _Optional[_Union[ConfigStatus, str]] = ..., listener_config: _Optional[_Union[_config_dump_pb2.ListenersConfigDump, _Mapping]] = ..., cluster_config: _Optional[_Union[_config_dump_pb2.ClustersConfigDump, _Mapping]] = ..., route_config: _Optional[_Union[_config_dump_pb2.RoutesConfigDump, _Mapping]] = ..., scoped_route_config: _Optional[_Union[_config_dump_pb2.ScopedRoutesConfigDump, _Mapping]] = ...) -> None: ...

class ClientConfig(_message.Message):
    __slots__ = ("node", "xds_config")
    NODE_FIELD_NUMBER: _ClassVar[int]
    XDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    xds_config: _containers.RepeatedCompositeFieldContainer[PerXdsConfig]
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., xds_config: _Optional[_Iterable[_Union[PerXdsConfig, _Mapping]]] = ...) -> None: ...

class ClientStatusResponse(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _containers.RepeatedCompositeFieldContainer[ClientConfig]
    def __init__(self, config: _Optional[_Iterable[_Union[ClientConfig, _Mapping]]] = ...) -> None: ...
