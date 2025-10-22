from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Composite(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FilterChainConfiguration(_message.Message):
    __slots__ = ("typed_config",)
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    typed_config: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    def __init__(self, typed_config: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ...) -> None: ...

class DynamicConfig(_message.Message):
    __slots__ = ("name", "config_discovery")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DISCOVERY_FIELD_NUMBER: _ClassVar[int]
    name: str
    config_discovery: _config_source_pb2.ExtensionConfigSource
    def __init__(self, name: _Optional[str] = ..., config_discovery: _Optional[_Union[_config_source_pb2.ExtensionConfigSource, _Mapping]] = ...) -> None: ...

class ExecuteFilterAction(_message.Message):
    __slots__ = ("typed_config", "dynamic_config", "filter_chain", "sample_percent")
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FILTER_CHAIN_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    typed_config: _extension_pb2.TypedExtensionConfig
    dynamic_config: DynamicConfig
    filter_chain: FilterChainConfiguration
    sample_percent: _base_pb2.RuntimeFractionalPercent
    def __init__(self, typed_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., dynamic_config: _Optional[_Union[DynamicConfig, _Mapping]] = ..., filter_chain: _Optional[_Union[FilterChainConfiguration, _Mapping]] = ..., sample_percent: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ...) -> None: ...
