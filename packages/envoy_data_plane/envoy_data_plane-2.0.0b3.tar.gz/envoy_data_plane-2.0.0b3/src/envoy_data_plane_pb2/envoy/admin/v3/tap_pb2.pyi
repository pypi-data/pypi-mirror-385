from envoy.config.tap.v3 import common_pb2 as _common_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TapRequest(_message.Message):
    __slots__ = ("config_id", "tap_config")
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    TAP_CONFIG_FIELD_NUMBER: _ClassVar[int]
    config_id: str
    tap_config: _common_pb2.TapConfig
    def __init__(self, config_id: _Optional[str] = ..., tap_config: _Optional[_Union[_common_pb2.TapConfig, _Mapping]] = ...) -> None: ...
