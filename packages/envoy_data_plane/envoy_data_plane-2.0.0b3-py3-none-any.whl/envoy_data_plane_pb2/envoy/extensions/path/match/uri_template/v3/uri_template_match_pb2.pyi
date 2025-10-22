from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UriTemplateMatchConfig(_message.Message):
    __slots__ = ("path_template",)
    PATH_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    path_template: str
    def __init__(self, path_template: _Optional[str] = ...) -> None: ...
