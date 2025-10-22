from google.protobuf import any_pb2 as _any_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApiListener(_message.Message):
    __slots__ = ("api_listener",)
    API_LISTENER_FIELD_NUMBER: _ClassVar[int]
    api_listener: _any_pb2.Any
    def __init__(self, api_listener: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
