from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CdnLoopConfig(_message.Message):
    __slots__ = ("cdn_id", "max_allowed_occurrences")
    CDN_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_ALLOWED_OCCURRENCES_FIELD_NUMBER: _ClassVar[int]
    cdn_id: str
    max_allowed_occurrences: int
    def __init__(self, cdn_id: _Optional[str] = ..., max_allowed_occurrences: _Optional[int] = ...) -> None: ...
