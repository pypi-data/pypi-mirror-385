from google.protobuf import any_pb2 as _any_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tracing(_message.Message):
    __slots__ = ("http",)
    class Http(_message.Message):
        __slots__ = ("name", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    HTTP_FIELD_NUMBER: _ClassVar[int]
    http: Tracing.Http
    def __init__(self, http: _Optional[_Union[Tracing.Http, _Mapping]] = ...) -> None: ...
