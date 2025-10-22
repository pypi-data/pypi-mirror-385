from envoy.config.rbac.v2 import rbac_pb2 as _rbac_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RBAC(_message.Message):
    __slots__ = ("rules", "shadow_rules", "stat_prefix", "enforcement_type")
    class EnforcementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ONE_TIME_ON_FIRST_BYTE: _ClassVar[RBAC.EnforcementType]
        CONTINUOUS: _ClassVar[RBAC.EnforcementType]
    ONE_TIME_ON_FIRST_BYTE: RBAC.EnforcementType
    CONTINUOUS: RBAC.EnforcementType
    RULES_FIELD_NUMBER: _ClassVar[int]
    SHADOW_RULES_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ENFORCEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    rules: _rbac_pb2.RBAC
    shadow_rules: _rbac_pb2.RBAC
    stat_prefix: str
    enforcement_type: RBAC.EnforcementType
    def __init__(self, rules: _Optional[_Union[_rbac_pb2.RBAC, _Mapping]] = ..., shadow_rules: _Optional[_Union[_rbac_pb2.RBAC, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., enforcement_type: _Optional[_Union[RBAC.EnforcementType, str]] = ...) -> None: ...
