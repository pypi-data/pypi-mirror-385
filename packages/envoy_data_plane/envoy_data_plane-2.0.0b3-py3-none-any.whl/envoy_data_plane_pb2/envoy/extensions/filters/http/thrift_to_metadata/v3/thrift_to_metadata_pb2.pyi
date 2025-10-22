from envoy.extensions.filters.network.thrift_proxy.v3 import thrift_proxy_pb2 as _thrift_proxy_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Field(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METHOD_NAME: _ClassVar[Field]
    PROTOCOL: _ClassVar[Field]
    TRANSPORT: _ClassVar[Field]
    HEADER_FLAGS: _ClassVar[Field]
    SEQUENCE_ID: _ClassVar[Field]
    MESSAGE_TYPE: _ClassVar[Field]
    REPLY_TYPE: _ClassVar[Field]
METHOD_NAME: Field
PROTOCOL: Field
TRANSPORT: Field
HEADER_FLAGS: Field
SEQUENCE_ID: Field
MESSAGE_TYPE: Field
REPLY_TYPE: Field

class KeyValuePair(_message.Message):
    __slots__ = ("metadata_namespace", "key", "value")
    METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    metadata_namespace: str
    key: str
    value: _struct_pb2.Value
    def __init__(self, metadata_namespace: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...

class FieldSelector(_message.Message):
    __slots__ = ("name", "id", "child")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    CHILD_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    child: FieldSelector
    def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ..., child: _Optional[_Union[FieldSelector, _Mapping]] = ...) -> None: ...

class Rule(_message.Message):
    __slots__ = ("field", "field_selector", "method_name", "on_present", "on_missing")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FIELD_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    METHOD_NAME_FIELD_NUMBER: _ClassVar[int]
    ON_PRESENT_FIELD_NUMBER: _ClassVar[int]
    ON_MISSING_FIELD_NUMBER: _ClassVar[int]
    field: Field
    field_selector: FieldSelector
    method_name: str
    on_present: KeyValuePair
    on_missing: KeyValuePair
    def __init__(self, field: _Optional[_Union[Field, str]] = ..., field_selector: _Optional[_Union[FieldSelector, _Mapping]] = ..., method_name: _Optional[str] = ..., on_present: _Optional[_Union[KeyValuePair, _Mapping]] = ..., on_missing: _Optional[_Union[KeyValuePair, _Mapping]] = ...) -> None: ...

class ThriftToMetadata(_message.Message):
    __slots__ = ("request_rules", "response_rules", "transport", "protocol", "allow_content_types", "allow_empty_content_type")
    REQUEST_RULES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_RULES_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CONTENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_EMPTY_CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    request_rules: _containers.RepeatedCompositeFieldContainer[Rule]
    response_rules: _containers.RepeatedCompositeFieldContainer[Rule]
    transport: _thrift_proxy_pb2.TransportType
    protocol: _thrift_proxy_pb2.ProtocolType
    allow_content_types: _containers.RepeatedScalarFieldContainer[str]
    allow_empty_content_type: bool
    def __init__(self, request_rules: _Optional[_Iterable[_Union[Rule, _Mapping]]] = ..., response_rules: _Optional[_Iterable[_Union[Rule, _Mapping]]] = ..., transport: _Optional[_Union[_thrift_proxy_pb2.TransportType, str]] = ..., protocol: _Optional[_Union[_thrift_proxy_pb2.ProtocolType, str]] = ..., allow_content_types: _Optional[_Iterable[str]] = ..., allow_empty_content_type: bool = ...) -> None: ...

class ThriftToMetadataPerRoute(_message.Message):
    __slots__ = ("request_rules", "response_rules")
    REQUEST_RULES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_RULES_FIELD_NUMBER: _ClassVar[int]
    request_rules: _containers.RepeatedCompositeFieldContainer[Rule]
    response_rules: _containers.RepeatedCompositeFieldContainer[Rule]
    def __init__(self, request_rules: _Optional[_Iterable[_Union[Rule, _Mapping]]] = ..., response_rules: _Optional[_Iterable[_Union[Rule, _Mapping]]] = ...) -> None: ...
