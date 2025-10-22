from envoy.type.matcher.v3 import regex_pb2 as _regex_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PayloadToMetadata(_message.Message):
    __slots__ = ("request_rules",)
    class ValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRING: _ClassVar[PayloadToMetadata.ValueType]
        NUMBER: _ClassVar[PayloadToMetadata.ValueType]
    STRING: PayloadToMetadata.ValueType
    NUMBER: PayloadToMetadata.ValueType
    class KeyValuePair(_message.Message):
        __slots__ = ("metadata_namespace", "key", "value", "regex_value_rewrite", "type")
        METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        REGEX_VALUE_REWRITE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        metadata_namespace: str
        key: str
        value: str
        regex_value_rewrite: _regex_pb2.RegexMatchAndSubstitute
        type: PayloadToMetadata.ValueType
        def __init__(self, metadata_namespace: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., regex_value_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., type: _Optional[_Union[PayloadToMetadata.ValueType, str]] = ...) -> None: ...
    class Rule(_message.Message):
        __slots__ = ("method_name", "service_name", "field_selector", "on_present", "on_missing")
        METHOD_NAME_FIELD_NUMBER: _ClassVar[int]
        SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        FIELD_SELECTOR_FIELD_NUMBER: _ClassVar[int]
        ON_PRESENT_FIELD_NUMBER: _ClassVar[int]
        ON_MISSING_FIELD_NUMBER: _ClassVar[int]
        method_name: str
        service_name: str
        field_selector: PayloadToMetadata.FieldSelector
        on_present: PayloadToMetadata.KeyValuePair
        on_missing: PayloadToMetadata.KeyValuePair
        def __init__(self, method_name: _Optional[str] = ..., service_name: _Optional[str] = ..., field_selector: _Optional[_Union[PayloadToMetadata.FieldSelector, _Mapping]] = ..., on_present: _Optional[_Union[PayloadToMetadata.KeyValuePair, _Mapping]] = ..., on_missing: _Optional[_Union[PayloadToMetadata.KeyValuePair, _Mapping]] = ...) -> None: ...
    class FieldSelector(_message.Message):
        __slots__ = ("name", "id", "child")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        CHILD_FIELD_NUMBER: _ClassVar[int]
        name: str
        id: int
        child: PayloadToMetadata.FieldSelector
        def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ..., child: _Optional[_Union[PayloadToMetadata.FieldSelector, _Mapping]] = ...) -> None: ...
    REQUEST_RULES_FIELD_NUMBER: _ClassVar[int]
    request_rules: _containers.RepeatedCompositeFieldContainer[PayloadToMetadata.Rule]
    def __init__(self, request_rules: _Optional[_Iterable[_Union[PayloadToMetadata.Rule, _Mapping]]] = ...) -> None: ...
