from envoy.type.matcher.v3 import regex_pb2 as _regex_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("request_rules", "response_rules", "stat_prefix")
    class ValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRING: _ClassVar[Config.ValueType]
        NUMBER: _ClassVar[Config.ValueType]
        PROTOBUF_VALUE: _ClassVar[Config.ValueType]
    STRING: Config.ValueType
    NUMBER: Config.ValueType
    PROTOBUF_VALUE: Config.ValueType
    class ValueEncode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[Config.ValueEncode]
        BASE64: _ClassVar[Config.ValueEncode]
    NONE: Config.ValueEncode
    BASE64: Config.ValueEncode
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
        type: Config.ValueType
        encode: Config.ValueEncode
        def __init__(self, metadata_namespace: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., regex_value_rewrite: _Optional[_Union[_regex_pb2.RegexMatchAndSubstitute, _Mapping]] = ..., type: _Optional[_Union[Config.ValueType, str]] = ..., encode: _Optional[_Union[Config.ValueEncode, str]] = ...) -> None: ...
    class Rule(_message.Message):
        __slots__ = ("header", "cookie", "on_header_present", "on_header_missing", "remove")
        HEADER_FIELD_NUMBER: _ClassVar[int]
        COOKIE_FIELD_NUMBER: _ClassVar[int]
        ON_HEADER_PRESENT_FIELD_NUMBER: _ClassVar[int]
        ON_HEADER_MISSING_FIELD_NUMBER: _ClassVar[int]
        REMOVE_FIELD_NUMBER: _ClassVar[int]
        header: str
        cookie: str
        on_header_present: Config.KeyValuePair
        on_header_missing: Config.KeyValuePair
        remove: bool
        def __init__(self, header: _Optional[str] = ..., cookie: _Optional[str] = ..., on_header_present: _Optional[_Union[Config.KeyValuePair, _Mapping]] = ..., on_header_missing: _Optional[_Union[Config.KeyValuePair, _Mapping]] = ..., remove: bool = ...) -> None: ...
    REQUEST_RULES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_RULES_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    request_rules: _containers.RepeatedCompositeFieldContainer[Config.Rule]
    response_rules: _containers.RepeatedCompositeFieldContainer[Config.Rule]
    stat_prefix: str
    def __init__(self, request_rules: _Optional[_Iterable[_Union[Config.Rule, _Mapping]]] = ..., response_rules: _Optional[_Iterable[_Union[Config.Rule, _Mapping]]] = ..., stat_prefix: _Optional[str] = ...) -> None: ...
