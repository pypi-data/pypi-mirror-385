from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RegexMatcher(_message.Message):
    __slots__ = ("google_re2", "regex")
    class GoogleRE2(_message.Message):
        __slots__ = ("max_program_size",)
        MAX_PROGRAM_SIZE_FIELD_NUMBER: _ClassVar[int]
        max_program_size: _wrappers_pb2.UInt32Value
        def __init__(self, max_program_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
    GOOGLE_RE2_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    google_re2: RegexMatcher.GoogleRE2
    regex: str
    def __init__(self, google_re2: _Optional[_Union[RegexMatcher.GoogleRE2, _Mapping]] = ..., regex: _Optional[str] = ...) -> None: ...

class RegexMatchAndSubstitute(_message.Message):
    __slots__ = ("pattern", "substitution")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    SUBSTITUTION_FIELD_NUMBER: _ClassVar[int]
    pattern: RegexMatcher
    substitution: str
    def __init__(self, pattern: _Optional[_Union[RegexMatcher, _Mapping]] = ..., substitution: _Optional[str] = ...) -> None: ...
