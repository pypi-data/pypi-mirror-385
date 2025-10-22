import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServiceAccountJwtAccessCredentials(_message.Message):
    __slots__ = ("json_key", "token_lifetime")
    JSON_KEY_FIELD_NUMBER: _ClassVar[int]
    TOKEN_LIFETIME_FIELD_NUMBER: _ClassVar[int]
    json_key: str
    token_lifetime: _duration_pb2.Duration
    def __init__(self, json_key: _Optional[str] = ..., token_lifetime: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
