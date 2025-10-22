from envoy.config.rbac.v2 import rbac_pb2 as _rbac_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RBAC(_message.Message):
    __slots__ = ("rules", "shadow_rules")
    RULES_FIELD_NUMBER: _ClassVar[int]
    SHADOW_RULES_FIELD_NUMBER: _ClassVar[int]
    rules: _rbac_pb2.RBAC
    shadow_rules: _rbac_pb2.RBAC
    def __init__(self, rules: _Optional[_Union[_rbac_pb2.RBAC, _Mapping]] = ..., shadow_rules: _Optional[_Union[_rbac_pb2.RBAC, _Mapping]] = ...) -> None: ...

class RBACPerRoute(_message.Message):
    __slots__ = ("rbac",)
    RBAC_FIELD_NUMBER: _ClassVar[int]
    rbac: RBAC
    def __init__(self, rbac: _Optional[_Union[RBAC, _Mapping]] = ...) -> None: ...
