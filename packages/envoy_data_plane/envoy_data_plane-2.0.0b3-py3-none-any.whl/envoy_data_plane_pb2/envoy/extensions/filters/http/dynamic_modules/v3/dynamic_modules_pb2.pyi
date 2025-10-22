from envoy.extensions.dynamic_modules.v3 import dynamic_modules_pb2 as _dynamic_modules_pb2
from google.protobuf import any_pb2 as _any_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DynamicModuleFilter(_message.Message):
    __slots__ = ("dynamic_module_config", "filter_name", "filter_config", "terminal_filter")
    DYNAMIC_MODULE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FILTER_NAME_FIELD_NUMBER: _ClassVar[int]
    FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_FILTER_FIELD_NUMBER: _ClassVar[int]
    dynamic_module_config: _dynamic_modules_pb2.DynamicModuleConfig
    filter_name: str
    filter_config: _any_pb2.Any
    terminal_filter: bool
    def __init__(self, dynamic_module_config: _Optional[_Union[_dynamic_modules_pb2.DynamicModuleConfig, _Mapping]] = ..., filter_name: _Optional[str] = ..., filter_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., terminal_filter: bool = ...) -> None: ...

class DynamicModuleFilterPerRoute(_message.Message):
    __slots__ = ("dynamic_module_config", "per_route_config_name", "filter_config")
    DYNAMIC_MODULE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PER_ROUTE_CONFIG_NAME_FIELD_NUMBER: _ClassVar[int]
    FILTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    dynamic_module_config: _dynamic_modules_pb2.DynamicModuleConfig
    per_route_config_name: str
    filter_config: _any_pb2.Any
    def __init__(self, dynamic_module_config: _Optional[_Union[_dynamic_modules_pb2.DynamicModuleConfig, _Mapping]] = ..., per_route_config_name: _Optional[str] = ..., filter_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
