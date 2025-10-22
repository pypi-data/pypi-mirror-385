from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Decompressor(_message.Message):
    __slots__ = ("decompressor_library", "request_direction_config", "response_direction_config")
    class CommonDirectionConfig(_message.Message):
        __slots__ = ("enabled", "ignore_no_transform_header")
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        IGNORE_NO_TRANSFORM_HEADER_FIELD_NUMBER: _ClassVar[int]
        enabled: _base_pb2.RuntimeFeatureFlag
        ignore_no_transform_header: bool
        def __init__(self, enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., ignore_no_transform_header: bool = ...) -> None: ...
    class RequestDirectionConfig(_message.Message):
        __slots__ = ("common_config", "advertise_accept_encoding")
        COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
        ADVERTISE_ACCEPT_ENCODING_FIELD_NUMBER: _ClassVar[int]
        common_config: Decompressor.CommonDirectionConfig
        advertise_accept_encoding: _wrappers_pb2.BoolValue
        def __init__(self, common_config: _Optional[_Union[Decompressor.CommonDirectionConfig, _Mapping]] = ..., advertise_accept_encoding: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
    class ResponseDirectionConfig(_message.Message):
        __slots__ = ("common_config",)
        COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
        common_config: Decompressor.CommonDirectionConfig
        def __init__(self, common_config: _Optional[_Union[Decompressor.CommonDirectionConfig, _Mapping]] = ...) -> None: ...
    DECOMPRESSOR_LIBRARY_FIELD_NUMBER: _ClassVar[int]
    REQUEST_DIRECTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_DIRECTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    decompressor_library: _extension_pb2.TypedExtensionConfig
    request_direction_config: Decompressor.RequestDirectionConfig
    response_direction_config: Decompressor.ResponseDirectionConfig
    def __init__(self, decompressor_library: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., request_direction_config: _Optional[_Union[Decompressor.RequestDirectionConfig, _Mapping]] = ..., response_direction_config: _Optional[_Union[Decompressor.ResponseDirectionConfig, _Mapping]] = ...) -> None: ...
