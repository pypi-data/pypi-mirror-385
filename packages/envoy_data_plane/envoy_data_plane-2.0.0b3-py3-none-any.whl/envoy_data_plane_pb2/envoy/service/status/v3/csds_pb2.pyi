import datetime

from envoy.admin.v3 import config_dump_shared_pb2 as _config_dump_shared_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.matcher.v3 import node_pb2 as _node_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
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

class ClientConfigStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLIENT_UNKNOWN: _ClassVar[ClientConfigStatus]
    CLIENT_REQUESTED: _ClassVar[ClientConfigStatus]
    CLIENT_ACKED: _ClassVar[ClientConfigStatus]
    CLIENT_NACKED: _ClassVar[ClientConfigStatus]
    CLIENT_RECEIVED_ERROR: _ClassVar[ClientConfigStatus]
UNKNOWN: ConfigStatus
SYNCED: ConfigStatus
NOT_SENT: ConfigStatus
STALE: ConfigStatus
ERROR: ConfigStatus
CLIENT_UNKNOWN: ClientConfigStatus
CLIENT_REQUESTED: ClientConfigStatus
CLIENT_ACKED: ClientConfigStatus
CLIENT_NACKED: ClientConfigStatus
CLIENT_RECEIVED_ERROR: ClientConfigStatus

class ClientStatusRequest(_message.Message):
    __slots__ = ("node_matchers", "node", "exclude_resource_contents")
    NODE_MATCHERS_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_RESOURCE_CONTENTS_FIELD_NUMBER: _ClassVar[int]
    node_matchers: _containers.RepeatedCompositeFieldContainer[_node_pb2.NodeMatcher]
    node: _base_pb2.Node
    exclude_resource_contents: bool
    def __init__(self, node_matchers: _Optional[_Iterable[_Union[_node_pb2.NodeMatcher, _Mapping]]] = ..., node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., exclude_resource_contents: bool = ...) -> None: ...

class PerXdsConfig(_message.Message):
    __slots__ = ("status", "client_status", "listener_config", "cluster_config", "route_config", "scoped_route_config", "endpoint_config")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
    LISTENER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SCOPED_ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    status: ConfigStatus
    client_status: ClientConfigStatus
    listener_config: _config_dump_shared_pb2.ListenersConfigDump
    cluster_config: _config_dump_shared_pb2.ClustersConfigDump
    route_config: _config_dump_shared_pb2.RoutesConfigDump
    scoped_route_config: _config_dump_shared_pb2.ScopedRoutesConfigDump
    endpoint_config: _config_dump_shared_pb2.EndpointsConfigDump
    def __init__(self, status: _Optional[_Union[ConfigStatus, str]] = ..., client_status: _Optional[_Union[ClientConfigStatus, str]] = ..., listener_config: _Optional[_Union[_config_dump_shared_pb2.ListenersConfigDump, _Mapping]] = ..., cluster_config: _Optional[_Union[_config_dump_shared_pb2.ClustersConfigDump, _Mapping]] = ..., route_config: _Optional[_Union[_config_dump_shared_pb2.RoutesConfigDump, _Mapping]] = ..., scoped_route_config: _Optional[_Union[_config_dump_shared_pb2.ScopedRoutesConfigDump, _Mapping]] = ..., endpoint_config: _Optional[_Union[_config_dump_shared_pb2.EndpointsConfigDump, _Mapping]] = ...) -> None: ...

class ClientConfig(_message.Message):
    __slots__ = ("node", "xds_config", "generic_xds_configs", "client_scope")
    class GenericXdsConfig(_message.Message):
        __slots__ = ("type_url", "name", "version_info", "xds_config", "last_updated", "config_status", "client_status", "error_state", "is_static_resource")
        TYPE_URL_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        XDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        CONFIG_STATUS_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        IS_STATIC_RESOURCE_FIELD_NUMBER: _ClassVar[int]
        type_url: str
        name: str
        version_info: str
        xds_config: _any_pb2.Any
        last_updated: _timestamp_pb2.Timestamp
        config_status: ConfigStatus
        client_status: _config_dump_shared_pb2.ClientResourceStatus
        error_state: _config_dump_shared_pb2.UpdateFailureState
        is_static_resource: bool
        def __init__(self, type_url: _Optional[str] = ..., name: _Optional[str] = ..., version_info: _Optional[str] = ..., xds_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., config_status: _Optional[_Union[ConfigStatus, str]] = ..., client_status: _Optional[_Union[_config_dump_shared_pb2.ClientResourceStatus, str]] = ..., error_state: _Optional[_Union[_config_dump_shared_pb2.UpdateFailureState, _Mapping]] = ..., is_static_resource: bool = ...) -> None: ...
    NODE_FIELD_NUMBER: _ClassVar[int]
    XDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    GENERIC_XDS_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SCOPE_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    xds_config: _containers.RepeatedCompositeFieldContainer[PerXdsConfig]
    generic_xds_configs: _containers.RepeatedCompositeFieldContainer[ClientConfig.GenericXdsConfig]
    client_scope: str
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., xds_config: _Optional[_Iterable[_Union[PerXdsConfig, _Mapping]]] = ..., generic_xds_configs: _Optional[_Iterable[_Union[ClientConfig.GenericXdsConfig, _Mapping]]] = ..., client_scope: _Optional[str] = ...) -> None: ...

class ClientStatusResponse(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _containers.RepeatedCompositeFieldContainer[ClientConfig]
    def __init__(self, config: _Optional[_Iterable[_Union[ClientConfig, _Mapping]]] = ...) -> None: ...
