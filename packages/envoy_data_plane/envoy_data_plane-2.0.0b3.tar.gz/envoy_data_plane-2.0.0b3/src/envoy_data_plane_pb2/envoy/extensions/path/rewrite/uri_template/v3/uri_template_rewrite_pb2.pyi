from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UriTemplateRewriteConfig(_message.Message):
    __slots__ = ("path_template_rewrite",)
    PATH_TEMPLATE_REWRITE_FIELD_NUMBER: _ClassVar[int]
    path_template_rewrite: str
    def __init__(self, path_template_rewrite: _Optional[str] = ...) -> None: ...
