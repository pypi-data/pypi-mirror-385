from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("arn", "payload_passthrough", "invocation_mode")
    class InvocationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SYNCHRONOUS: _ClassVar[Config.InvocationMode]
        ASYNCHRONOUS: _ClassVar[Config.InvocationMode]
    SYNCHRONOUS: Config.InvocationMode
    ASYNCHRONOUS: Config.InvocationMode
    ARN_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_PASSTHROUGH_FIELD_NUMBER: _ClassVar[int]
    INVOCATION_MODE_FIELD_NUMBER: _ClassVar[int]
    arn: str
    payload_passthrough: bool
    invocation_mode: Config.InvocationMode
    def __init__(self, arn: _Optional[str] = ..., payload_passthrough: bool = ..., invocation_mode: _Optional[_Union[Config.InvocationMode, str]] = ...) -> None: ...

class PerRouteConfig(_message.Message):
    __slots__ = ("invoke_config",)
    INVOKE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    invoke_config: Config
    def __init__(self, invoke_config: _Optional[_Union[Config, _Mapping]] = ...) -> None: ...
