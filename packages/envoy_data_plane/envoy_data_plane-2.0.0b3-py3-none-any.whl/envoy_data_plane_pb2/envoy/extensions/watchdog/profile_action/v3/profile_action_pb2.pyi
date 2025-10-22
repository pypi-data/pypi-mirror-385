import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProfileActionConfig(_message.Message):
    __slots__ = ("profile_duration", "profile_path", "max_profiles")
    PROFILE_DURATION_FIELD_NUMBER: _ClassVar[int]
    PROFILE_PATH_FIELD_NUMBER: _ClassVar[int]
    MAX_PROFILES_FIELD_NUMBER: _ClassVar[int]
    profile_duration: _duration_pb2.Duration
    profile_path: str
    max_profiles: int
    def __init__(self, profile_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., profile_path: _Optional[str] = ..., max_profiles: _Optional[int] = ...) -> None: ...
