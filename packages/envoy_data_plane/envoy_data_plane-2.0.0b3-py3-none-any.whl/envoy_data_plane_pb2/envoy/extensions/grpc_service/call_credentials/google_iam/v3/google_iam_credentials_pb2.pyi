from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GoogleIamCredentials(_message.Message):
    __slots__ = ("authorization_token", "authority_selector")
    AUTHORIZATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    AUTHORITY_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    authorization_token: str
    authority_selector: str
    def __init__(self, authorization_token: _Optional[str] = ..., authority_selector: _Optional[str] = ...) -> None: ...
