from envoy.type.v3 import percent_pb2 as _percent_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KillRequest(_message.Message):
    __slots__ = ("probability", "kill_request_header", "direction")
    class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REQUEST: _ClassVar[KillRequest.Direction]
        RESPONSE: _ClassVar[KillRequest.Direction]
    REQUEST: KillRequest.Direction
    RESPONSE: KillRequest.Direction
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    KILL_REQUEST_HEADER_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    probability: _percent_pb2.FractionalPercent
    kill_request_header: str
    direction: KillRequest.Direction
    def __init__(self, probability: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., kill_request_header: _Optional[str] = ..., direction: _Optional[_Union[KillRequest.Direction, str]] = ...) -> None: ...
