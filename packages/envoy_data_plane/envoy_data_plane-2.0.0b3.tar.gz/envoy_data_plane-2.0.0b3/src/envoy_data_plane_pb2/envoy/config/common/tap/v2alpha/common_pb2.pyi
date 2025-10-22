from envoy.service.tap.v2alpha import common_pb2 as _common_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommonExtensionConfig(_message.Message):
    __slots__ = ("admin_config", "static_config")
    ADMIN_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STATIC_CONFIG_FIELD_NUMBER: _ClassVar[int]
    admin_config: AdminConfig
    static_config: _common_pb2.TapConfig
    def __init__(self, admin_config: _Optional[_Union[AdminConfig, _Mapping]] = ..., static_config: _Optional[_Union[_common_pb2.TapConfig, _Mapping]] = ...) -> None: ...

class AdminConfig(_message.Message):
    __slots__ = ("config_id",)
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    config_id: str
    def __init__(self, config_id: _Optional[str] = ...) -> None: ...
