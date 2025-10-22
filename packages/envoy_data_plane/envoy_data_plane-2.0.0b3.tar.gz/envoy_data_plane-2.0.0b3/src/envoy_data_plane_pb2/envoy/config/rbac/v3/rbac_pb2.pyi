from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.type.matcher.v3 import filter_state_pb2 as _filter_state_pb2
from envoy.type.matcher.v3 import metadata_pb2 as _metadata_pb2
from envoy.type.matcher.v3 import path_pb2 as _path_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from envoy.type.v3 import range_pb2 as _range_pb2
from google.api.expr.v1alpha1 import checked_pb2 as _checked_pb2
from google.api.expr.v1alpha1 import syntax_pb2 as _syntax_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MetadataSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DYNAMIC: _ClassVar[MetadataSource]
    ROUTE: _ClassVar[MetadataSource]
DYNAMIC: MetadataSource
ROUTE: MetadataSource

class RBAC(_message.Message):
    __slots__ = ("action", "policies", "audit_logging_options")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALLOW: _ClassVar[RBAC.Action]
        DENY: _ClassVar[RBAC.Action]
        LOG: _ClassVar[RBAC.Action]
    ALLOW: RBAC.Action
    DENY: RBAC.Action
    LOG: RBAC.Action
    class AuditLoggingOptions(_message.Message):
        __slots__ = ("audit_condition", "logger_configs")
        class AuditCondition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NONE: _ClassVar[RBAC.AuditLoggingOptions.AuditCondition]
            ON_DENY: _ClassVar[RBAC.AuditLoggingOptions.AuditCondition]
            ON_ALLOW: _ClassVar[RBAC.AuditLoggingOptions.AuditCondition]
            ON_DENY_AND_ALLOW: _ClassVar[RBAC.AuditLoggingOptions.AuditCondition]
        NONE: RBAC.AuditLoggingOptions.AuditCondition
        ON_DENY: RBAC.AuditLoggingOptions.AuditCondition
        ON_ALLOW: RBAC.AuditLoggingOptions.AuditCondition
        ON_DENY_AND_ALLOW: RBAC.AuditLoggingOptions.AuditCondition
        class AuditLoggerConfig(_message.Message):
            __slots__ = ("audit_logger", "is_optional")
            AUDIT_LOGGER_FIELD_NUMBER: _ClassVar[int]
            IS_OPTIONAL_FIELD_NUMBER: _ClassVar[int]
            audit_logger: _extension_pb2.TypedExtensionConfig
            is_optional: bool
            def __init__(self, audit_logger: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., is_optional: bool = ...) -> None: ...
        AUDIT_CONDITION_FIELD_NUMBER: _ClassVar[int]
        LOGGER_CONFIGS_FIELD_NUMBER: _ClassVar[int]
        audit_condition: RBAC.AuditLoggingOptions.AuditCondition
        logger_configs: _containers.RepeatedCompositeFieldContainer[RBAC.AuditLoggingOptions.AuditLoggerConfig]
        def __init__(self, audit_condition: _Optional[_Union[RBAC.AuditLoggingOptions.AuditCondition, str]] = ..., logger_configs: _Optional[_Iterable[_Union[RBAC.AuditLoggingOptions.AuditLoggerConfig, _Mapping]]] = ...) -> None: ...
    class PoliciesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Policy
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Policy, _Mapping]] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    AUDIT_LOGGING_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    action: RBAC.Action
    policies: _containers.MessageMap[str, Policy]
    audit_logging_options: RBAC.AuditLoggingOptions
    def __init__(self, action: _Optional[_Union[RBAC.Action, str]] = ..., policies: _Optional[_Mapping[str, Policy]] = ..., audit_logging_options: _Optional[_Union[RBAC.AuditLoggingOptions, _Mapping]] = ...) -> None: ...

class Policy(_message.Message):
    __slots__ = ("permissions", "principals", "condition", "checked_condition")
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    PRINCIPALS_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    CHECKED_CONDITION_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    principals: _containers.RepeatedCompositeFieldContainer[Principal]
    condition: _syntax_pb2.Expr
    checked_condition: _checked_pb2.CheckedExpr
    def __init__(self, permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ..., principals: _Optional[_Iterable[_Union[Principal, _Mapping]]] = ..., condition: _Optional[_Union[_syntax_pb2.Expr, _Mapping]] = ..., checked_condition: _Optional[_Union[_checked_pb2.CheckedExpr, _Mapping]] = ...) -> None: ...

class SourcedMetadata(_message.Message):
    __slots__ = ("metadata_matcher", "metadata_source")
    METADATA_MATCHER_FIELD_NUMBER: _ClassVar[int]
    METADATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    metadata_matcher: _metadata_pb2.MetadataMatcher
    metadata_source: MetadataSource
    def __init__(self, metadata_matcher: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., metadata_source: _Optional[_Union[MetadataSource, str]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("and_rules", "or_rules", "any", "header", "url_path", "destination_ip", "destination_port", "destination_port_range", "metadata", "not_rule", "requested_server_name", "matcher", "uri_template", "sourced_metadata")
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
    DESTINATION_PORT_RANGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NOT_RULE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    URI_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    SOURCED_METADATA_FIELD_NUMBER: _ClassVar[int]
    and_rules: Permission.Set
    or_rules: Permission.Set
    any: bool
    header: _route_components_pb2.HeaderMatcher
    url_path: _path_pb2.PathMatcher
    destination_ip: _address_pb2.CidrRange
    destination_port: int
    destination_port_range: _range_pb2.Int32Range
    metadata: _metadata_pb2.MetadataMatcher
    not_rule: Permission
    requested_server_name: _string_pb2.StringMatcher
    matcher: _extension_pb2.TypedExtensionConfig
    uri_template: _extension_pb2.TypedExtensionConfig
    sourced_metadata: SourcedMetadata
    def __init__(self, and_rules: _Optional[_Union[Permission.Set, _Mapping]] = ..., or_rules: _Optional[_Union[Permission.Set, _Mapping]] = ..., any: bool = ..., header: _Optional[_Union[_route_components_pb2.HeaderMatcher, _Mapping]] = ..., url_path: _Optional[_Union[_path_pb2.PathMatcher, _Mapping]] = ..., destination_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., destination_port: _Optional[int] = ..., destination_port_range: _Optional[_Union[_range_pb2.Int32Range, _Mapping]] = ..., metadata: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., not_rule: _Optional[_Union[Permission, _Mapping]] = ..., requested_server_name: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., matcher: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., uri_template: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., sourced_metadata: _Optional[_Union[SourcedMetadata, _Mapping]] = ...) -> None: ...

class Principal(_message.Message):
    __slots__ = ("and_ids", "or_ids", "any", "authenticated", "source_ip", "direct_remote_ip", "remote_ip", "header", "url_path", "metadata", "filter_state", "not_id", "sourced_metadata", "custom")
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
    FILTER_STATE_FIELD_NUMBER: _ClassVar[int]
    NOT_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCED_METADATA_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_FIELD_NUMBER: _ClassVar[int]
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
    filter_state: _filter_state_pb2.FilterStateMatcher
    not_id: Principal
    sourced_metadata: SourcedMetadata
    custom: _extension_pb2.TypedExtensionConfig
    def __init__(self, and_ids: _Optional[_Union[Principal.Set, _Mapping]] = ..., or_ids: _Optional[_Union[Principal.Set, _Mapping]] = ..., any: bool = ..., authenticated: _Optional[_Union[Principal.Authenticated, _Mapping]] = ..., source_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., direct_remote_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., remote_ip: _Optional[_Union[_address_pb2.CidrRange, _Mapping]] = ..., header: _Optional[_Union[_route_components_pb2.HeaderMatcher, _Mapping]] = ..., url_path: _Optional[_Union[_path_pb2.PathMatcher, _Mapping]] = ..., metadata: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., filter_state: _Optional[_Union[_filter_state_pb2.FilterStateMatcher, _Mapping]] = ..., not_id: _Optional[_Union[Principal, _Mapping]] = ..., sourced_metadata: _Optional[_Union[SourcedMetadata, _Mapping]] = ..., custom: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...

class Action(_message.Message):
    __slots__ = ("name", "action")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    action: RBAC.Action
    def __init__(self, name: _Optional[str] = ..., action: _Optional[_Union[RBAC.Action, str]] = ...) -> None: ...
