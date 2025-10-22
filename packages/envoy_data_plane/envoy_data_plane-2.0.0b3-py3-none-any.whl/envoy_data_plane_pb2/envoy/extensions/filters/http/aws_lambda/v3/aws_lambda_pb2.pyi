from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("arn", "payload_passthrough", "invocation_mode", "host_rewrite", "credentials_profile", "credentials")
    class InvocationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SYNCHRONOUS: _ClassVar[Config.InvocationMode]
        ASYNCHRONOUS: _ClassVar[Config.InvocationMode]
    SYNCHRONOUS: Config.InvocationMode
    ASYNCHRONOUS: Config.InvocationMode
    ARN_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_PASSTHROUGH_FIELD_NUMBER: _ClassVar[int]
    INVOCATION_MODE_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_PROFILE_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    arn: str
    payload_passthrough: bool
    invocation_mode: Config.InvocationMode
    host_rewrite: str
    credentials_profile: str
    credentials: Credentials
    def __init__(self, arn: _Optional[str] = ..., payload_passthrough: bool = ..., invocation_mode: _Optional[_Union[Config.InvocationMode, str]] = ..., host_rewrite: _Optional[str] = ..., credentials_profile: _Optional[str] = ..., credentials: _Optional[_Union[Credentials, _Mapping]] = ...) -> None: ...

class Credentials(_message.Message):
    __slots__ = ("access_key_id", "secret_access_key", "session_token")
    ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_key_id: str
    secret_access_key: str
    session_token: str
    def __init__(self, access_key_id: _Optional[str] = ..., secret_access_key: _Optional[str] = ..., session_token: _Optional[str] = ...) -> None: ...

class PerRouteConfig(_message.Message):
    __slots__ = ("invoke_config",)
    INVOKE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    invoke_config: Config
    def __init__(self, invoke_config: _Optional[_Union[Config, _Mapping]] = ...) -> None: ...
