from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.matcher.v3 import regex_pb2 as _regex_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HeaderMutationRules(_message.Message):
    __slots__ = ("allow_all_routing", "allow_envoy", "disallow_system", "disallow_all", "allow_expression", "disallow_expression", "disallow_is_error")
    ALLOW_ALL_ROUTING_FIELD_NUMBER: _ClassVar[int]
    ALLOW_ENVOY_FIELD_NUMBER: _ClassVar[int]
    DISALLOW_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    DISALLOW_ALL_FIELD_NUMBER: _ClassVar[int]
    ALLOW_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    DISALLOW_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    DISALLOW_IS_ERROR_FIELD_NUMBER: _ClassVar[int]
    allow_all_routing: _wrappers_pb2.BoolValue
    allow_envoy: _wrappers_pb2.BoolValue
    disallow_system: _wrappers_pb2.BoolValue
    disallow_all: _wrappers_pb2.BoolValue
    allow_expression: _regex_pb2.RegexMatcher
    disallow_expression: _regex_pb2.RegexMatcher
    disallow_is_error: _wrappers_pb2.BoolValue
    def __init__(self, allow_all_routing: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., allow_envoy: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., disallow_system: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., disallow_all: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., allow_expression: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., disallow_expression: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., disallow_is_error: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class HeaderMutation(_message.Message):
    __slots__ = ("remove", "append", "remove_on_match")
    class RemoveOnMatch(_message.Message):
        __slots__ = ("key_matcher",)
        KEY_MATCHER_FIELD_NUMBER: _ClassVar[int]
        key_matcher: _string_pb2.StringMatcher
        def __init__(self, key_matcher: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ...) -> None: ...
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    APPEND_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ON_MATCH_FIELD_NUMBER: _ClassVar[int]
    remove: str
    append: _base_pb2.HeaderValueOption
    remove_on_match: HeaderMutation.RemoveOnMatch
    def __init__(self, remove: _Optional[str] = ..., append: _Optional[_Union[_base_pb2.HeaderValueOption, _Mapping]] = ..., remove_on_match: _Optional[_Union[HeaderMutation.RemoveOnMatch, _Mapping]] = ...) -> None: ...
