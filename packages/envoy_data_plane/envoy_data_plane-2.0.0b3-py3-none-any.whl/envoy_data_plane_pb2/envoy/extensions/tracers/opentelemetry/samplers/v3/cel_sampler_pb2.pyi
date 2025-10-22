from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.type.v3 import cel_pb2 as _cel_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CELSamplerConfig(_message.Message):
    __slots__ = ("expression",)
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    expression: _cel_pb2.CelExpression
    def __init__(self, expression: _Optional[_Union[_cel_pb2.CelExpression, _Mapping]] = ...) -> None: ...
