from test.fuzz import common_pb2 as _common_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GolangFilterTestCase(_message.Message):
    __slots__ = ("request_data",)
    REQUEST_DATA_FIELD_NUMBER: _ClassVar[int]
    request_data: _common_pb2.HttpData
    def __init__(self, request_data: _Optional[_Union[_common_pb2.HttpData, _Mapping]] = ...) -> None: ...
