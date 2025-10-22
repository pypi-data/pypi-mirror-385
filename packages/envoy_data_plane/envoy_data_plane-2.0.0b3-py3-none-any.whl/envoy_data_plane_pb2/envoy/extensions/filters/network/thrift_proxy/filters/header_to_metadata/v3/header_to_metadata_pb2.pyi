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

class HeaderToMetadata(_message.Message):
    __slots__ = ("request_rules",)
    class ValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRING: _ClassVar[HeaderToMetadata.ValueType]
        NUMBER: _ClassVar[HeaderToMetadata.ValueType]
        PROTOBUF_VALUE: _ClassVar[HeaderToMetadata.ValueType]
    STRING: HeaderToMetadata.ValueType
    NUMBER: HeaderToMetadata.ValueType
    PROTOBUF_VALUE: HeaderToMetadata.ValueType
    class ValueEncode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[HeaderToMetadata.ValueEncode]
        BASE64: _ClassVar[HeaderToMetadata.ValueEncode]
    NONE: HeaderToMetadata.ValueEncode
    BASE64: HeaderToMetadata.ValueEncode
    class KeyValuePair(_message.Message):
        __slots__ = ("metadata_namespace", "key", "value", "regex_value_rewrite", "type", "encode")
        METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        REGEX_VALUE_REWRITE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        ENCODE_FIELD_NUMBER: _ClassVar[int]
        metadata_namespace: str
        key: str
        value: str
        regex_value_rewrite: _regex_pb2.RegexMatchAndSubstitute
        type: HeaderToMetadata.ValueType
        encode: HeaderToMetadata.ValueEncode
        def __init__(self, metadata_namespace: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., regex_value_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., type: _Optional[_Union[HeaderToMetadata.ValueType, str]] = ..., encode: _Optional[_Union[HeaderToMetadata.ValueEncode, str]] = ...) -> None: ...
    class Rule(_message.Message):
        __slots__ = ("header", "on_present", "on_missing", "remove")
        HEADER_FIELD_NUMBER: _ClassVar[int]
        ON_PRESENT_FIELD_NUMBER: _ClassVar[int]
        ON_MISSING_FIELD_NUMBER: _ClassVar[int]
        REMOVE_FIELD_NUMBER: _ClassVar[int]
        header: str
        on_present: HeaderToMetadata.KeyValuePair
        on_missing: HeaderToMetadata.KeyValuePair
        remove: bool
        def __init__(self, header: _Optional[str] = ..., on_present: _Optional[_Union[HeaderToMetadata.KeyValuePair, _Mapping]] = ..., on_missing: _Optional[_Union[HeaderToMetadata.KeyValuePair, _Mapping]] = ..., remove: bool = ...) -> None: ...
    REQUEST_RULES_FIELD_NUMBER: _ClassVar[int]
    request_rules: _containers.RepeatedCompositeFieldContainer[HeaderToMetadata.Rule]
    def __init__(self, request_rules: _Optional[_Iterable[_Union[HeaderToMetadata.Rule, _Mapping]]] = ...) -> None: ...
