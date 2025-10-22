from envoy.config.core.v3 import base_pb2 as _base_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProtoMessageExtractionConfig(_message.Message):
    __slots__ = ("data_source", "proto_descriptor_typed_metadata", "mode", "extraction_by_method")
    class ExtractMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ExtractMode_UNSPECIFIED: _ClassVar[ProtoMessageExtractionConfig.ExtractMode]
        FIRST_AND_LAST: _ClassVar[ProtoMessageExtractionConfig.ExtractMode]
    ExtractMode_UNSPECIFIED: ProtoMessageExtractionConfig.ExtractMode
    FIRST_AND_LAST: ProtoMessageExtractionConfig.ExtractMode
    class ExtractionByMethodEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MethodExtraction
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MethodExtraction, _Mapping]] = ...) -> None: ...
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    PROTO_DESCRIPTOR_TYPED_METADATA_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    EXTRACTION_BY_METHOD_FIELD_NUMBER: _ClassVar[int]
    data_source: _base_pb2.DataSource
    proto_descriptor_typed_metadata: str
    mode: ProtoMessageExtractionConfig.ExtractMode
    extraction_by_method: _containers.MessageMap[str, MethodExtraction]
    def __init__(self, data_source: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., proto_descriptor_typed_metadata: _Optional[str] = ..., mode: _Optional[_Union[ProtoMessageExtractionConfig.ExtractMode, str]] = ..., extraction_by_method: _Optional[_Mapping[str, MethodExtraction]] = ...) -> None: ...

class MethodExtraction(_message.Message):
    __slots__ = ("request_extraction_by_field", "response_extraction_by_field")
    class ExtractDirective(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ExtractDirective_UNSPECIFIED: _ClassVar[MethodExtraction.ExtractDirective]
        EXTRACT: _ClassVar[MethodExtraction.ExtractDirective]
        EXTRACT_REDACT: _ClassVar[MethodExtraction.ExtractDirective]
    ExtractDirective_UNSPECIFIED: MethodExtraction.ExtractDirective
    EXTRACT: MethodExtraction.ExtractDirective
    EXTRACT_REDACT: MethodExtraction.ExtractDirective
    class RequestExtractionByFieldEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MethodExtraction.ExtractDirective
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MethodExtraction.ExtractDirective, str]] = ...) -> None: ...
    class ResponseExtractionByFieldEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MethodExtraction.ExtractDirective
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MethodExtraction.ExtractDirective, str]] = ...) -> None: ...
    REQUEST_EXTRACTION_BY_FIELD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_EXTRACTION_BY_FIELD_FIELD_NUMBER: _ClassVar[int]
    request_extraction_by_field: _containers.ScalarMap[str, MethodExtraction.ExtractDirective]
    response_extraction_by_field: _containers.ScalarMap[str, MethodExtraction.ExtractDirective]
    def __init__(self, request_extraction_by_field: _Optional[_Mapping[str, MethodExtraction.ExtractDirective]] = ..., response_extraction_by_field: _Optional[_Mapping[str, MethodExtraction.ExtractDirective]] = ...) -> None: ...
