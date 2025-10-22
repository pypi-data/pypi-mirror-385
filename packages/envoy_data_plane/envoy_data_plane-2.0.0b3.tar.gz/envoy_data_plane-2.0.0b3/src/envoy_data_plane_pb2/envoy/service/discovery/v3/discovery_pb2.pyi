import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.rpc import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceLocator(_message.Message):
    __slots__ = ("name", "dynamic_parameters")
    class DynamicParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    dynamic_parameters: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., dynamic_parameters: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ResourceName(_message.Message):
    __slots__ = ("name", "dynamic_parameter_constraints")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_PARAMETER_CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    dynamic_parameter_constraints: DynamicParameterConstraints
    def __init__(self, name: _Optional[str] = ..., dynamic_parameter_constraints: _Optional[_Union[DynamicParameterConstraints, _Mapping]] = ...) -> None: ...

class ResourceError(_message.Message):
    __slots__ = ("resource_name", "error_detail")
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    resource_name: ResourceName
    error_detail: _status_pb2.Status
    def __init__(self, resource_name: _Optional[_Union[ResourceName, _Mapping]] = ..., error_detail: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class DiscoveryRequest(_message.Message):
    __slots__ = ("version_info", "node", "resource_names", "resource_locators", "type_url", "response_nonce", "error_detail")
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_LOCATORS_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_NONCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    version_info: str
    node: _base_pb2.Node
    resource_names: _containers.RepeatedScalarFieldContainer[str]
    resource_locators: _containers.RepeatedCompositeFieldContainer[ResourceLocator]
    type_url: str
    response_nonce: str
    error_detail: _status_pb2.Status
    def __init__(self, version_info: _Optional[str] = ..., node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., resource_names: _Optional[_Iterable[str]] = ..., resource_locators: _Optional[_Iterable[_Union[ResourceLocator, _Mapping]]] = ..., type_url: _Optional[str] = ..., response_nonce: _Optional[str] = ..., error_detail: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class DiscoveryResponse(_message.Message):
    __slots__ = ("version_info", "resources", "canary", "type_url", "nonce", "control_plane", "resource_errors")
    VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    CANARY_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_PLANE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ERRORS_FIELD_NUMBER: _ClassVar[int]
    version_info: str
    resources: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    canary: bool
    type_url: str
    nonce: str
    control_plane: _base_pb2.ControlPlane
    resource_errors: _containers.RepeatedCompositeFieldContainer[ResourceError]
    def __init__(self, version_info: _Optional[str] = ..., resources: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ..., canary: bool = ..., type_url: _Optional[str] = ..., nonce: _Optional[str] = ..., control_plane: _Optional[_Union[_base_pb2.ControlPlane, _Mapping]] = ..., resource_errors: _Optional[_Iterable[_Union[ResourceError, _Mapping]]] = ...) -> None: ...

class DeltaDiscoveryRequest(_message.Message):
    __slots__ = ("node", "type_url", "resource_names_subscribe", "resource_names_unsubscribe", "resource_locators_subscribe", "resource_locators_unsubscribe", "initial_resource_versions", "response_nonce", "error_detail")
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
    RESOURCE_LOCATORS_SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_LOCATORS_UNSUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_RESOURCE_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_NONCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    node: _base_pb2.Node
    type_url: str
    resource_names_subscribe: _containers.RepeatedScalarFieldContainer[str]
    resource_names_unsubscribe: _containers.RepeatedScalarFieldContainer[str]
    resource_locators_subscribe: _containers.RepeatedCompositeFieldContainer[ResourceLocator]
    resource_locators_unsubscribe: _containers.RepeatedCompositeFieldContainer[ResourceLocator]
    initial_resource_versions: _containers.ScalarMap[str, str]
    response_nonce: str
    error_detail: _status_pb2.Status
    def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., type_url: _Optional[str] = ..., resource_names_subscribe: _Optional[_Iterable[str]] = ..., resource_names_unsubscribe: _Optional[_Iterable[str]] = ..., resource_locators_subscribe: _Optional[_Iterable[_Union[ResourceLocator, _Mapping]]] = ..., resource_locators_unsubscribe: _Optional[_Iterable[_Union[ResourceLocator, _Mapping]]] = ..., initial_resource_versions: _Optional[_Mapping[str, str]] = ..., response_nonce: _Optional[str] = ..., error_detail: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class DeltaDiscoveryResponse(_message.Message):
    __slots__ = ("system_version_info", "resources", "type_url", "removed_resources", "removed_resource_names", "nonce", "control_plane", "resource_errors")
    SYSTEM_VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    REMOVED_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    REMOVED_RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_PLANE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ERRORS_FIELD_NUMBER: _ClassVar[int]
    system_version_info: str
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    type_url: str
    removed_resources: _containers.RepeatedScalarFieldContainer[str]
    removed_resource_names: _containers.RepeatedCompositeFieldContainer[ResourceName]
    nonce: str
    control_plane: _base_pb2.ControlPlane
    resource_errors: _containers.RepeatedCompositeFieldContainer[ResourceError]
    def __init__(self, system_version_info: _Optional[str] = ..., resources: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ..., type_url: _Optional[str] = ..., removed_resources: _Optional[_Iterable[str]] = ..., removed_resource_names: _Optional[_Iterable[_Union[ResourceName, _Mapping]]] = ..., nonce: _Optional[str] = ..., control_plane: _Optional[_Union[_base_pb2.ControlPlane, _Mapping]] = ..., resource_errors: _Optional[_Iterable[_Union[ResourceError, _Mapping]]] = ...) -> None: ...

class DynamicParameterConstraints(_message.Message):
    __slots__ = ("constraint", "or_constraints", "and_constraints", "not_constraints")
    class SingleConstraint(_message.Message):
        __slots__ = ("key", "value", "exists")
        class Exists(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        EXISTS_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        exists: DynamicParameterConstraints.SingleConstraint.Exists
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ..., exists: _Optional[_Union[DynamicParameterConstraints.SingleConstraint.Exists, _Mapping]] = ...) -> None: ...
    class ConstraintList(_message.Message):
        __slots__ = ("constraints",)
        CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
        constraints: _containers.RepeatedCompositeFieldContainer[DynamicParameterConstraints]
        def __init__(self, constraints: _Optional[_Iterable[_Union[DynamicParameterConstraints, _Mapping]]] = ...) -> None: ...
    CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    OR_CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    AND_CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    NOT_CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    constraint: DynamicParameterConstraints.SingleConstraint
    or_constraints: DynamicParameterConstraints.ConstraintList
    and_constraints: DynamicParameterConstraints.ConstraintList
    not_constraints: DynamicParameterConstraints
    def __init__(self, constraint: _Optional[_Union[DynamicParameterConstraints.SingleConstraint, _Mapping]] = ..., or_constraints: _Optional[_Union[DynamicParameterConstraints.ConstraintList, _Mapping]] = ..., and_constraints: _Optional[_Union[DynamicParameterConstraints.ConstraintList, _Mapping]] = ..., not_constraints: _Optional[_Union[DynamicParameterConstraints, _Mapping]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("name", "resource_name", "aliases", "version", "resource", "ttl", "cache_control", "metadata")
    class CacheControl(_message.Message):
        __slots__ = ("do_not_cache",)
        DO_NOT_CACHE_FIELD_NUMBER: _ClassVar[int]
        do_not_cache: bool
        def __init__(self, do_not_cache: bool = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    TTL_FIELD_NUMBER: _ClassVar[int]
    CACHE_CONTROL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    resource_name: ResourceName
    aliases: _containers.RepeatedScalarFieldContainer[str]
    version: str
    resource: _any_pb2.Any
    ttl: _duration_pb2.Duration
    cache_control: Resource.CacheControl
    metadata: _base_pb2.Metadata
    def __init__(self, name: _Optional[str] = ..., resource_name: _Optional[_Union[ResourceName, _Mapping]] = ..., aliases: _Optional[_Iterable[str]] = ..., version: _Optional[str] = ..., resource: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., cache_control: _Optional[_Union[Resource.CacheControl, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...
