from google.api.expr.v1alpha1 import syntax_pb2 as _syntax_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Descriptor(_message.Message):
    __slots__ = ("descriptor_key", "skip_if_error", "text", "parsed")
    DESCRIPTOR_KEY_FIELD_NUMBER: _ClassVar[int]
    SKIP_IF_ERROR_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PARSED_FIELD_NUMBER: _ClassVar[int]
    descriptor_key: str
    skip_if_error: bool
    text: str
    parsed: _syntax_pb2.Expr
    def __init__(self, descriptor_key: _Optional[str] = ..., skip_if_error: bool = ..., text: _Optional[str] = ..., parsed: _Optional[_Union[_syntax_pb2.Expr, _Mapping]] = ...) -> None: ...
