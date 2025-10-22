from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.route import route_components_pb2 as _route_components_pb2
from envoy.type.matcher import metadata_pb2 as _metadata_pb2
from envoy.type.matcher import path_pb2 as _path_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from google.api.expr.v1alpha1 import syntax_pb2 as _syntax_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RBAC(_message.Message):
    __slots__ = ("action", "policies")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALLOW: _ClassVar[RBAC.Action]
        DENY: _ClassVar[RBAC.Action]
    ALLOW: RBAC.Action
    DENY: RBAC.Action
    class PoliciesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Policy
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Policy, _Mapping]] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    action: RBAC.Action
    policies: _containers.MessageMap[str, Policy]
    def __init__(self, action: _Optional[_Union[RBAC.Action, str]] = ..., policies: _Optional[_Mapping[str, Policy]] = ...) -> None: ...

class Policy(_message.Message):
    __slots__ = ("permissions", "principals", "condition")
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    PRINCIPALS_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    principals: _containers.RepeatedCompositeFieldContainer[Principal]
    condition: _syntax_pb2.Expr
    def __init__(self, permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ..., principals: _Optional[_Iterable[_Union[Principal, _Mapping]]] = ..., condition: _Optional[_Union[_syntax_pb2.Expr, _Mapping]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("and_rules", "or_rules", "any", "header", "url_path", "destination_ip", "destination_port", "metadata", "not_rule", "requested_server_name")
    class Set(_message.Message):
        __slots__ = ("rules",)
        RULES_FIELD_NUMBER: _ClassVar[int]
        rules: _containers.RepeatedCompositeFieldContainer[Permission]
        def __init__(self, rules: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ...) -> None: ...
    AND_RULES_FIELD_NUMBER: _ClassVar[int]
    OR_RULES_FIELD_NUMBER: _ClassVar[int]
    ANY_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    URL_PATH_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_IP_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NOT_RULE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    and_rules: Permission.Set
    or_rules: Permission.Set
    any: bool
    header: _route_components_pb2.HeaderMatcher
    url_path: _path_pb2.PathMatcher
    destination_ip: _address_pb2.CidrRange
    destination_port: int
    metadata: _metadata_pb2.MetadataMatcher
    not_rule: Permission
    requested_server_name: _string_pb2.StringMatcher
    def __init__(self, and_rules: _Optional[_Union[Permission.Set, _Mapping]] = ..., or_rules: _Optional[_Union[Permission.Set, _Mapping]] = ..., any: bool = ..., header: _Optional[_Union[_route_components_pb2.HeaderMatcher, _Mapping]] = ..., url_path: _Optional[_Union[_path_pb2.PathMatcher, _Mapping]] = ..., destination_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., destination_port: _Optional[int] = ..., metadata: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., not_rule: _Optional[_Union[Permission, _Mapping]] = ..., requested_server_name: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ...) -> None: ...

class Principal(_message.Message):
    __slots__ = ("and_ids", "or_ids", "any", "authenticated", "source_ip", "direct_remote_ip", "remote_ip", "header", "url_path", "metadata", "not_id")
    class Set(_message.Message):
        __slots__ = ("ids",)
        IDS_FIELD_NUMBER: _ClassVar[int]
        ids: _containers.RepeatedCompositeFieldContainer[Principal]
        def __init__(self, ids: _Optional[_Iterable[_Union[Principal, _Mapping]]] = ...) -> None: ...
    class Authenticated(_message.Message):
        __slots__ = ("principal_name",)
        PRINCIPAL_NAME_FIELD_NUMBER: _ClassVar[int]
        principal_name: _string_pb2.StringMatcher
        def __init__(self, principal_name: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ...) -> None: ...
    AND_IDS_FIELD_NUMBER: _ClassVar[int]
    OR_IDS_FIELD_NUMBER: _ClassVar[int]
    ANY_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATED_FIELD_NUMBER: _ClassVar[int]
    SOURCE_IP_FIELD_NUMBER: _ClassVar[int]
    DIRECT_REMOTE_IP_FIELD_NUMBER: _ClassVar[int]
    REMOTE_IP_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    URL_PATH_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NOT_ID_FIELD_NUMBER: _ClassVar[int]
    and_ids: Principal.Set
    or_ids: Principal.Set
    any: bool
    authenticated: Principal.Authenticated
    source_ip: _address_pb2.CidrRange
    direct_remote_ip: _address_pb2.CidrRange
    remote_ip: _address_pb2.CidrRange
    header: _route_components_pb2.HeaderMatcher
    url_path: _path_pb2.PathMatcher
    metadata: _metadata_pb2.MetadataMatcher
    not_id: Principal
    def __init__(self, and_ids: _Optional[_Union[Principal.Set, _Mapping]] = ..., or_ids: _Optional[_Union[Principal.Set, _Mapping]] = ..., any: bool = ..., authenticated: _Optional[_Union[Principal.Authenticated, _Mapping]] = ..., source_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., direct_remote_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., remote_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., header: _Optional[_Union[_route_components_pb2.HeaderMatcher, _Mapping]] = ..., url_path: _Optional[_Union[_path_pb2.PathMatcher, _Mapping]] = ..., metadata: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., not_id: _Optional[_Union[Principal, _Mapping]] = ...) -> None: ...
