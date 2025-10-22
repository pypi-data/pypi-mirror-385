from envoy.type.matcher import regex_pb2 as _regex_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StringMatcher(_message.Message):
    __slots__ = ("exact", "prefix", "suffix", "regex", "safe_regex", "ignore_case")
    EXACT_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    SAFE_REGEX_FIELD_NUMBER: _ClassVar[int]
    IGNORE_CASE_FIELD_NUMBER: _ClassVar[int]
    exact: str
    prefix: str
    suffix: str
    regex: str
    safe_regex: _regex_pb2.RegexMatcher
    ignore_case: bool
    def __init__(self, exact: _Optional[str] = ..., prefix: _Optional[str] = ..., suffix: _Optional[str] = ..., regex: _Optional[str] = ..., safe_regex: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ..., ignore_case: bool = ...) -> None: ...

class ListStringMatcher(_message.Message):
    __slots__ = ("patterns",)
    PATTERNS_FIELD_NUMBER: _ClassVar[int]
    patterns: _containers.RepeatedCompositeFieldContainer[StringMatcher]
    def __init__(self, patterns: _Optional[_Iterable[_Union[StringMatcher, _Mapping]]] = ...) -> None: ...
