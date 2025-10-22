from envoy.type.matcher.v3 import value_pb2 as _value_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Metadata(_message.Message):
    __slots__ = ("value", "invert")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    INVERT_FIELD_NUMBER: _ClassVar[int]
    value: _value_pb2.ValueMatcher
    invert: bool
    def __init__(self, value: _Optional[_Union[_value_pb2.ValueMatcher, _Mapping]] = ..., invert: bool = ...) -> None: ...
