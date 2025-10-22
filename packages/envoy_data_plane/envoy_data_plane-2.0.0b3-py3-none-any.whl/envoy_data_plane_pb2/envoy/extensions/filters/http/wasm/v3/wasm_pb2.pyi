from envoy.extensions.wasm.v3 import wasm_pb2 as _wasm_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Wasm(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _wasm_pb2.PluginConfig
    def __init__(self, config: _Optional[_Union[_wasm_pb2.PluginConfig, _Mapping]] = ...) -> None: ...
