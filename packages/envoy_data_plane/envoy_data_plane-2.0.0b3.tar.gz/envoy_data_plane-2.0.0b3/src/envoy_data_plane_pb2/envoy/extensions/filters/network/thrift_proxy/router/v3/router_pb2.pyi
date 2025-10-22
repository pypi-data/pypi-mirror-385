from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Router(_message.Message):
    __slots__ = ("close_downstream_on_upstream_error",)
    CLOSE_DOWNSTREAM_ON_UPSTREAM_ERROR_FIELD_NUMBER: _ClassVar[int]
    close_downstream_on_upstream_error: _wrappers_pb2.BoolValue
    def __init__(self, close_downstream_on_upstream_error: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
