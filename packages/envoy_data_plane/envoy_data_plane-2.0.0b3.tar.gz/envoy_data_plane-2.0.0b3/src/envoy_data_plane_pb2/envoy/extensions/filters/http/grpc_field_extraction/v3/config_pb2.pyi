from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GrpcFieldExtractionConfig(_message.Message):
    __slots__ = ("descriptor_set", "extractions_by_method")
    class ExtractionsByMethodEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FieldExtractions
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FieldExtractions, _Mapping]] = ...) -> None: ...
    DESCRIPTOR_SET_FIELD_NUMBER: _ClassVar[int]
    EXTRACTIONS_BY_METHOD_FIELD_NUMBER: _ClassVar[int]
    descriptor_set: _base_pb2.DataSource
    extractions_by_method: _containers.MessageMap[str, FieldExtractions]
    def __init__(self, descriptor_set: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., extractions_by_method: _Optional[_Mapping[str, FieldExtractions]] = ...) -> None: ...

class FieldExtractions(_message.Message):
    __slots__ = ("request_field_extractions",)
    class RequestFieldExtractionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RequestFieldValueDisposition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RequestFieldValueDisposition, _Mapping]] = ...) -> None: ...
    REQUEST_FIELD_EXTRACTIONS_FIELD_NUMBER: _ClassVar[int]
    request_field_extractions: _containers.MessageMap[str, RequestFieldValueDisposition]
    def __init__(self, request_field_extractions: _Optional[_Mapping[str, RequestFieldValueDisposition]] = ...) -> None: ...

class RequestFieldValueDisposition(_message.Message):
    __slots__ = ("dynamic_metadata",)
    DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
    dynamic_metadata: str
    def __init__(self, dynamic_metadata: _Optional[str] = ...) -> None: ...
