from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SimpleMetric(_message.Message):
    __slots__ = ("type", "value", "name")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COUNTER: _ClassVar[SimpleMetric.Type]
        GAUGE: _ClassVar[SimpleMetric.Type]
    COUNTER: SimpleMetric.Type
    GAUGE: SimpleMetric.Type
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    type: SimpleMetric.Type
    value: int
    name: str
    def __init__(self, type: _Optional[_Union[SimpleMetric.Type, str]] = ..., value: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...
