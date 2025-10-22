from envoy.config.rbac.v3 import rbac_pb2 as _rbac_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RBAC(_message.Message):
    __slots__ = ("rules", "rules_stat_prefix", "matcher", "shadow_rules", "shadow_matcher", "shadow_rules_stat_prefix", "track_per_rule_stats")
    RULES_FIELD_NUMBER: _ClassVar[int]
    RULES_STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    SHADOW_RULES_FIELD_NUMBER: _ClassVar[int]
    SHADOW_MATCHER_FIELD_NUMBER: _ClassVar[int]
    SHADOW_RULES_STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    TRACK_PER_RULE_STATS_FIELD_NUMBER: _ClassVar[int]
    rules: _rbac_pb2.RBAC
    rules_stat_prefix: str
    matcher: _matcher_pb2.Matcher
    shadow_rules: _rbac_pb2.RBAC
    shadow_matcher: _matcher_pb2.Matcher
    shadow_rules_stat_prefix: str
    track_per_rule_stats: bool
    def __init__(self, rules: _Optional[_Union[_rbac_pb2.RBAC, _Mapping]] = ..., rules_stat_prefix: _Optional[str] = ..., matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., shadow_rules: _Optional[_Union[_rbac_pb2.RBAC, _Mapping]] = ..., shadow_matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., shadow_rules_stat_prefix: _Optional[str] = ..., track_per_rule_stats: bool = ...) -> None: ...

class RBACPerRoute(_message.Message):
    __slots__ = ("rbac",)
    RBAC_FIELD_NUMBER: _ClassVar[int]
    rbac: RBAC
    def __init__(self, rbac: _Optional[_Union[RBAC, _Mapping]] = ...) -> None: ...
