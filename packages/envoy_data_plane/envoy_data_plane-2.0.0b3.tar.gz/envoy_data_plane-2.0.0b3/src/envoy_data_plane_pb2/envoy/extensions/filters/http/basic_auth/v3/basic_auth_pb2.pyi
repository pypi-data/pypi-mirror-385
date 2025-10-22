from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BasicAuth(_message.Message):
    __slots__ = ("users", "forward_username_header", "authentication_header")
    USERS_FIELD_NUMBER: _ClassVar[int]
    FORWARD_USERNAME_HEADER_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_HEADER_FIELD_NUMBER: _ClassVar[int]
    users: _base_pb2.DataSource
    forward_username_header: str
    authentication_header: str
    def __init__(self, users: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., forward_username_header: _Optional[str] = ..., authentication_header: _Optional[str] = ...) -> None: ...

class BasicAuthPerRoute(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _base_pb2.DataSource
    def __init__(self, users: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
