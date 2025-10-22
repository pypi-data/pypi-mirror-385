from envoy.type.matcher import number_pb2 as _number_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValueMatcher(_message.Message):
    __slots__ = ("null_match", "double_match", "string_match", "bool_match", "present_match", "list_match")
    class NullMatch(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    NULL_MATCH_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_MATCH_FIELD_NUMBER: _ClassVar[int]
    STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    BOOL_MATCH_FIELD_NUMBER: _ClassVar[int]
    PRESENT_MATCH_FIELD_NUMBER: _ClassVar[int]
    LIST_MATCH_FIELD_NUMBER: _ClassVar[int]
    null_match: ValueMatcher.NullMatch
    double_match: _number_pb2.DoubleMatcher
    string_match: _string_pb2.StringMatcher
    bool_match: bool
    present_match: bool
    list_match: ListMatcher
    def __init__(self, null_match: _Optional[_Union[ValueMatcher.NullMatch, _Mapping]] = ..., double_match: _Optional[_Union[_number_pb2.DoubleMatcher, _Mapping]] = ..., string_match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., bool_match: bool = ..., present_match: bool = ..., list_match: _Optional[_Union[ListMatcher, _Mapping]] = ...) -> None: ...

class ListMatcher(_message.Message):
    __slots__ = ("one_of",)
    ONE_OF_FIELD_NUMBER: _ClassVar[int]
    one_of: ValueMatcher
    def __init__(self, one_of: _Optional[_Union[ValueMatcher, _Mapping]] = ...) -> None: ...
