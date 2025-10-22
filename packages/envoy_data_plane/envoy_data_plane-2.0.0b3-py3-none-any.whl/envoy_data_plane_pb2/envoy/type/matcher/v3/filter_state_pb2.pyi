from envoy.type.matcher.v3 import address_pb2 as _address_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterStateMatcher(_message.Message):
    __slots__ = ("key", "string_match", "address_match")
    KEY_FIELD_NUMBER: _ClassVar[int]
    STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_MATCH_FIELD_NUMBER: _ClassVar[int]
    key: str
    string_match: _string_pb2.StringMatcher
    address_match: _address_pb2.AddressMatcher
    def __init__(self, key: _Optional[str] = ..., string_match: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., address_match: _Optional[_Union[_address_pb2.AddressMatcher, _Mapping]] = ...) -> None: ...
