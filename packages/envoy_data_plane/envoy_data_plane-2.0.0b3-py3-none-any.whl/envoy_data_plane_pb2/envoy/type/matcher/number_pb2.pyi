from envoy.type import range_pb2 as _range_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DoubleMatcher(_message.Message):
    __slots__ = ("range", "exact")
    RANGE_FIELD_NUMBER: _ClassVar[int]
    EXACT_FIELD_NUMBER: _ClassVar[int]
    range: _range_pb2.DoubleRange
    exact: float
    def __init__(self, range: _Optional[_Union[_range_pb2.DoubleRange, _Mapping]] = ..., exact: _Optional[float] = ...) -> None: ...
