from envoy.type.matcher.v3 import regex_pb2 as _regex_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JsonToMetadata(_message.Message):
    __slots__ = ("request_rules", "response_rules")
    class ValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PROTOBUF_VALUE: _ClassVar[JsonToMetadata.ValueType]
        STRING: _ClassVar[JsonToMetadata.ValueType]
        NUMBER: _ClassVar[JsonToMetadata.ValueType]
    PROTOBUF_VALUE: JsonToMetadata.ValueType
    STRING: JsonToMetadata.ValueType
    NUMBER: JsonToMetadata.ValueType
    class KeyValuePair(_message.Message):
        __slots__ = ("metadata_namespace", "key", "value", "type", "preserve_existing_metadata_value")
        METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        PRESERVE_EXISTING_METADATA_VALUE_FIELD_NUMBER: _ClassVar[int]
        metadata_namespace: str
        key: str
        value: _struct_pb2.Value
        type: JsonToMetadata.ValueType
        preserve_existing_metadata_value: bool
        def __init__(self, metadata_namespace: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., type: _Optional[_Union[JsonToMetadata.ValueType, str]] = ..., preserve_existing_metadata_value: bool = ...) -> None: ...
    class Selector(_message.Message):
        __slots__ = ("key",)
        KEY_FIELD_NUMBER: _ClassVar[int]
        key: str
        def __init__(self, key: _Optional[str] = ...) -> None: ...
    class Rule(_message.Message):
        __slots__ = ("selectors", "on_present", "on_missing", "on_error")
        SELECTORS_FIELD_NUMBER: _ClassVar[int]
        ON_PRESENT_FIELD_NUMBER: _ClassVar[int]
        ON_MISSING_FIELD_NUMBER: _ClassVar[int]
        ON_ERROR_FIELD_NUMBER: _ClassVar[int]
        selectors: _containers.RepeatedCompositeFieldContainer[JsonToMetadata.Selector]
        on_present: JsonToMetadata.KeyValuePair
        on_missing: JsonToMetadata.KeyValuePair
        on_error: JsonToMetadata.KeyValuePair
        def __init__(self, selectors: _Optional[_Iterable[_Union[JsonToMetadata.Selector, _Mapping]]] = ..., on_present: _Optional[_Union[JsonToMetadata.KeyValuePair, _Mapping]] = ..., on_missing: _Optional[_Union[JsonToMetadata.KeyValuePair, _Mapping]] = ..., on_error: _Optional[_Union[JsonToMetadata.KeyValuePair, _Mapping]] = ...) -> None: ...
    class MatchRules(_message.Message):
        __slots__ = ("rules", "allow_content_types", "allow_empty_content_type", "allow_content_types_regex")
        RULES_FIELD_NUMBER: _ClassVar[int]
        ALLOW_CONTENT_TYPES_FIELD_NUMBER: _ClassVar[int]
        ALLOW_EMPTY_CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        ALLOW_CONTENT_TYPES_REGEX_FIELD_NUMBER: _ClassVar[int]
        rules: _containers.RepeatedCompositeFieldContainer[JsonToMetadata.Rule]
        allow_content_types: _containers.RepeatedScalarFieldContainer[str]
        allow_empty_content_type: bool
        allow_content_types_regex: _regex_pb2.RegexMatcher
        def __init__(self, rules: _Optional[_Iterable[_Union[JsonToMetadata.Rule, _Mapping]]] = ..., allow_content_types: _Optional[_Iterable[str]] = ..., allow_empty_content_type: bool = ..., allow_content_types_regex: _Optional[_Union[_regex_pb2.RegexMatcher, _Mapping]] = ...) -> None: ...
    REQUEST_RULES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_RULES_FIELD_NUMBER: _ClassVar[int]
    request_rules: JsonToMetadata.MatchRules
    response_rules: JsonToMetadata.MatchRules
    def __init__(self, request_rules: _Optional[_Union[JsonToMetadata.MatchRules, _Mapping]] = ..., response_rules: _Optional[_Union[JsonToMetadata.MatchRules, _Mapping]] = ...) -> None: ...
