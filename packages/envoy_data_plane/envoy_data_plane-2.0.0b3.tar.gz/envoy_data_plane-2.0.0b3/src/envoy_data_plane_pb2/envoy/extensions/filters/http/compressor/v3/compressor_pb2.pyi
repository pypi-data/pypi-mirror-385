from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Compressor(_message.Message):
    __slots__ = ("content_length", "content_type", "disable_on_etag_header", "remove_accept_encoding_header", "runtime_enabled", "compressor_library", "request_direction_config", "response_direction_config", "choose_first")
    class CommonDirectionConfig(_message.Message):
        __slots__ = ("enabled", "min_content_length", "content_type")
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        MIN_CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
        CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        enabled: _base_pb2.RuntimeFeatureFlag
        min_content_length: _wrappers_pb2.UInt32Value
        content_type: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., min_content_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., content_type: _Optional[_Iterable[str]] = ...) -> None: ...
    class RequestDirectionConfig(_message.Message):
        __slots__ = ("common_config",)
        COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
        common_config: Compressor.CommonDirectionConfig
        def __init__(self, common_config: _Optional[_Union[Compressor.CommonDirectionConfig, _Mapping]] = ...) -> None: ...
    class ResponseDirectionConfig(_message.Message):
        __slots__ = ("common_config", "disable_on_etag_header", "remove_accept_encoding_header", "uncompressible_response_codes", "status_header_enabled")
        COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
        DISABLE_ON_ETAG_HEADER_FIELD_NUMBER: _ClassVar[int]
        REMOVE_ACCEPT_ENCODING_HEADER_FIELD_NUMBER: _ClassVar[int]
        UNCOMPRESSIBLE_RESPONSE_CODES_FIELD_NUMBER: _ClassVar[int]
        STATUS_HEADER_ENABLED_FIELD_NUMBER: _ClassVar[int]
        common_config: Compressor.CommonDirectionConfig
        disable_on_etag_header: bool
        remove_accept_encoding_header: bool
        uncompressible_response_codes: _containers.RepeatedScalarFieldContainer[int]
        status_header_enabled: bool
        def __init__(self, common_config: _Optional[_Union[Compressor.CommonDirectionConfig, _Mapping]] = ..., disable_on_etag_header: bool = ..., remove_accept_encoding_header: bool = ..., uncompressible_response_codes: _Optional[_Iterable[int]] = ..., status_header_enabled: bool = ...) -> None: ...
    CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ON_ETAG_HEADER_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ACCEPT_ENCODING_HEADER_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    COMPRESSOR_LIBRARY_FIELD_NUMBER: _ClassVar[int]
    REQUEST_DIRECTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_DIRECTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CHOOSE_FIRST_FIELD_NUMBER: _ClassVar[int]
    content_length: _wrappers_pb2.UInt32Value
    content_type: _containers.RepeatedScalarFieldContainer[str]
    disable_on_etag_header: bool
    remove_accept_encoding_header: bool
    runtime_enabled: _base_pb2.RuntimeFeatureFlag
    compressor_library: _extension_pb2.TypedExtensionConfig
    request_direction_config: Compressor.RequestDirectionConfig
    response_direction_config: Compressor.ResponseDirectionConfig
    choose_first: bool
    def __init__(self, content_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., content_type: _Optional[_Iterable[str]] = ..., disable_on_etag_header: bool = ..., remove_accept_encoding_header: bool = ..., runtime_enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., compressor_library: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., request_direction_config: _Optional[_Union[Compressor.RequestDirectionConfig, _Mapping]] = ..., response_direction_config: _Optional[_Union[Compressor.ResponseDirectionConfig, _Mapping]] = ..., choose_first: bool = ...) -> None: ...

class ResponseDirectionOverrides(_message.Message):
    __slots__ = ("remove_accept_encoding_header",)
    REMOVE_ACCEPT_ENCODING_HEADER_FIELD_NUMBER: _ClassVar[int]
    remove_accept_encoding_header: _wrappers_pb2.BoolValue
    def __init__(self, remove_accept_encoding_header: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class CompressorOverrides(_message.Message):
    __slots__ = ("response_direction_config", "compressor_library")
    RESPONSE_DIRECTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    COMPRESSOR_LIBRARY_FIELD_NUMBER: _ClassVar[int]
    response_direction_config: ResponseDirectionOverrides
    compressor_library: _extension_pb2.TypedExtensionConfig
    def __init__(self, response_direction_config: _Optional[_Union[ResponseDirectionOverrides, _Mapping]] = ..., compressor_library: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...

class CompressorPerRoute(_message.Message):
    __slots__ = ("disabled", "overrides")
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    disabled: bool
    overrides: CompressorOverrides
    def __init__(self, disabled: bool = ..., overrides: _Optional[_Union[CompressorOverrides, _Mapping]] = ...) -> None: ...
