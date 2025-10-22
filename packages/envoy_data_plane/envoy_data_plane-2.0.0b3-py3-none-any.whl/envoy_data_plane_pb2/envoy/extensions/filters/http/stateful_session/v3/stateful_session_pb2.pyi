from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatefulSession(_message.Message):
    __slots__ = ("session_state", "strict", "stat_prefix")
    SESSION_STATE_FIELD_NUMBER: _ClassVar[int]
    STRICT_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    session_state: _extension_pb2.TypedExtensionConfig
    strict: bool
    stat_prefix: str
    def __init__(self, session_state: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., strict: bool = ..., stat_prefix: _Optional[str] = ...) -> None: ...

class StatefulSessionPerRoute(_message.Message):
    __slots__ = ("disabled", "stateful_session")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    STATEFUL_SESSION_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    stateful_session: StatefulSession
    def __init__(self, disabled: bool = ..., stateful_session: _Optional[_Union[StatefulSession, _Mapping]] = ...) -> None: ...
