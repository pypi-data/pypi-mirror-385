from envoy.config.core.v3 import substitution_format_string_pb2 as _substitution_format_string_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterStateValue(_message.Message):
    __slots__ = ("object_key", "factory_key", "format_string", "read_only", "shared_with_upstream", "skip_if_empty")
    class SharedWithUpstream(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[FilterStateValue.SharedWithUpstream]
        ONCE: _ClassVar[FilterStateValue.SharedWithUpstream]
        TRANSITIVE: _ClassVar[FilterStateValue.SharedWithUpstream]
    NONE: FilterStateValue.SharedWithUpstream
    ONCE: FilterStateValue.SharedWithUpstream
    TRANSITIVE: FilterStateValue.SharedWithUpstream
    OBJECT_KEY_FIELD_NUMBER: _ClassVar[int]
    FACTORY_KEY_FIELD_NUMBER: _ClassVar[int]
    FORMAT_STRING_FIELD_NUMBER: _ClassVar[int]
    READ_ONLY_FIELD_NUMBER: _ClassVar[int]
    SHARED_WITH_UPSTREAM_FIELD_NUMBER: _ClassVar[int]
    SKIP_IF_EMPTY_FIELD_NUMBER: _ClassVar[int]
    object_key: str
    factory_key: str
    format_string: _substitution_format_string_pb2.SubstitutionFormatString
    read_only: bool
    shared_with_upstream: FilterStateValue.SharedWithUpstream
    skip_if_empty: bool
    def __init__(self, object_key: _Optional[str] = ..., factory_key: _Optional[str] = ..., format_string: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ..., read_only: bool = ..., shared_with_upstream: _Optional[_Union[FilterStateValue.SharedWithUpstream, str]] = ..., skip_if_empty: bool = ...) -> None: ...
