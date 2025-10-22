from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.rpc import status_pb2 as _status_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DiscoveryRequest(_message.Message):
    __slots__ = ("version_info", "node", "resource_names", "type_url", "response_nonce", "error_detail")
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_NONCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    version_info: str
    node: _base_pb2.Node
    resource_names: _containers.RepeatedScalarFieldContainer[str]
    type_url: str
    response_nonce: str
    error_detail: _status_pb2.Status
    def __init__(self, version_info: _Optional[str] = ..., node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., resource_names: _Optional[_Iterable[str]] = ..., type_url: _Optional[str] = ..., response_nonce: _Optional[str] = ..., error_detail: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class DiscoveryResponse(_message.Message):
    __slots__ = ("version_info", "resources", "canary", "type_url", "nonce", "control_plane")
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    CANARY_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_PLANE_FIELD_NUMBER: _ClassVar[int]
    version_info: str
    resources: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    canary: bool
    type_url: str
    nonce: str
    control_plane: _base_pb2.ControlPlane
    def __init__(self, version_info: _Optional[str] = ..., resources: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ..., canary: bool = ..., type_url: _Optional[str] = ..., nonce: _Optional[str] = ..., control_plane: _Optional[_Union[_base_pb2.ControlPlane, _Mapping]] = ...) -> None: ...

class DeltaDiscoveryRequest(_message.Message):
    __slots__ = ("node", "type_url", "resource_names_subscribe", "resource_names_unsubscribe", "initial_resource_versions", "response_nonce", "error_detail")
    class InitialResourceVersionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_UNSUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_RESOURCE_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_NONCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    type_url: str
    resource_names_subscribe: _containers.RepeatedScalarFieldContainer[str]
    resource_names_unsubscribe: _containers.RepeatedScalarFieldContainer[str]
    initial_resource_versions: _containers.ScalarMap[str, str]
    response_nonce: str
    error_detail: _status_pb2.Status
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., type_url: _Optional[str] = ..., resource_names_subscribe: _Optional[_Iterable[str]] = ..., resource_names_unsubscribe: _Optional[_Iterable[str]] = ..., initial_resource_versions: _Optional[_Mapping[str, str]] = ..., response_nonce: _Optional[str] = ..., error_detail: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class DeltaDiscoveryResponse(_message.Message):
    __slots__ = ("system_version_info", "resources", "type_url", "removed_resources", "nonce")
    SYSTEM_VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    REMOVED_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    system_version_info: str
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    type_url: str
    removed_resources: _containers.RepeatedScalarFieldContainer[str]
    nonce: str
    def __init__(self, system_version_info: _Optional[str] = ..., resources: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ..., type_url: _Optional[str] = ..., removed_resources: _Optional[_Iterable[str]] = ..., nonce: _Optional[str] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("name", "aliases", "version", "resource")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    name: str
    aliases: _containers.RepeatedScalarFieldContainer[str]
    version: str
    resource: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., aliases: _Optional[_Iterable[str]] = ..., version: _Optional[str] = ..., resource: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
