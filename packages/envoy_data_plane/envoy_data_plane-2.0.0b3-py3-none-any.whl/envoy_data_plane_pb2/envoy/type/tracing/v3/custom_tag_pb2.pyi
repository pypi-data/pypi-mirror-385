from envoy.type.metadata.v3 import metadata_pb2 as _metadata_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CustomTag(_message.Message):
    __slots__ = ("tag", "literal", "environment", "request_header", "metadata")
    class Literal(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: str
        def __init__(self, value: _Optional[str] = ...) -> None: ...
    class Environment(_message.Message):
        __slots__ = ("name", "default_value")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        default_value: str
        def __init__(self, name: _Optional[str] = ..., default_value: _Optional[str] = ...) -> None: ...
    class Header(_message.Message):
        __slots__ = ("name", "default_value")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        default_value: str
        def __init__(self, name: _Optional[str] = ..., default_value: _Optional[str] = ...) -> None: ...
    class Metadata(_message.Message):
        __slots__ = ("kind", "metadata_key", "default_value")
        KIND_FIELD_NUMBER: _ClassVar[int]
        METADATA_KEY_FIELD_NUMBER: _ClassVar[int]
        DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
        kind: _metadata_pb2.MetadataKind
        metadata_key: _metadata_pb2.MetadataKey
        default_value: str
        def __init__(self, kind: _Optional[_Union[_metadata_pb2.MetadataKind, _Mapping]] = ..., metadata_key: _Optional[_Union[_metadata_pb2.MetadataKey, _Mapping]] = ..., default_value: _Optional[str] = ...) -> None: ...
    TAG_FIELD_NUMBER: _ClassVar[int]
    LITERAL_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    tag: str
    literal: CustomTag.Literal
    environment: CustomTag.Environment
    request_header: CustomTag.Header
    metadata: CustomTag.Metadata
    def __init__(self, tag: _Optional[str] = ..., literal: _Optional[_Union[CustomTag.Literal, _Mapping]] = ..., environment: _Optional[_Union[CustomTag.Environment, _Mapping]] = ..., request_header: _Optional[_Union[CustomTag.Header, _Mapping]] = ..., metadata: _Optional[_Union[CustomTag.Metadata, _Mapping]] = ...) -> None: ...
