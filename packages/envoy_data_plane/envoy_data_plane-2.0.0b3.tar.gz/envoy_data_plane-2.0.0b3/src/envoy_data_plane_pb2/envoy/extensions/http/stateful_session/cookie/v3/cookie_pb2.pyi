from envoy.type.http.v3 import cookie_pb2 as _cookie_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CookieBasedSessionState(_message.Message):
    __slots__ = ("cookie",)
    COOKIE_FIELD_NUMBER: _ClassVar[int]
    cookie: _cookie_pb2.Cookie
    def __init__(self, cookie: _Optional[_Union[_cookie_pb2.Cookie, _Mapping]] = ...) -> None: ...
