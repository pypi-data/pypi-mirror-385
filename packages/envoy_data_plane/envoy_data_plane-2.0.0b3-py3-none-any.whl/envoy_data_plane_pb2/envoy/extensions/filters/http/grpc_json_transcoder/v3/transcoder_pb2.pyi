from google.protobuf import wrappers_pb2 as _wrappers_pb2
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

class GrpcJsonTranscoder(_message.Message):
    __slots__ = ("proto_descriptor", "proto_descriptor_bin", "services", "print_options", "match_incoming_request_route", "ignored_query_parameters", "auto_mapping", "ignore_unknown_query_parameters", "convert_grpc_status", "url_unescape_spec", "query_param_unescape_plus", "match_unregistered_custom_verb", "request_validation_options", "case_insensitive_enum_parsing", "max_request_body_size", "max_response_body_size", "capture_unknown_query_parameters")
    class UrlUnescapeSpec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALL_CHARACTERS_EXCEPT_RESERVED: _ClassVar[GrpcJsonTranscoder.UrlUnescapeSpec]
        ALL_CHARACTERS_EXCEPT_SLASH: _ClassVar[GrpcJsonTranscoder.UrlUnescapeSpec]
        ALL_CHARACTERS: _ClassVar[GrpcJsonTranscoder.UrlUnescapeSpec]
    ALL_CHARACTERS_EXCEPT_RESERVED: GrpcJsonTranscoder.UrlUnescapeSpec
    ALL_CHARACTERS_EXCEPT_SLASH: GrpcJsonTranscoder.UrlUnescapeSpec
    ALL_CHARACTERS: GrpcJsonTranscoder.UrlUnescapeSpec
    class PrintOptions(_message.Message):
        __slots__ = ("add_whitespace", "always_print_primitive_fields", "always_print_enums_as_ints", "preserve_proto_field_names", "stream_newline_delimited", "stream_sse_style_delimited")
        ADD_WHITESPACE_FIELD_NUMBER: _ClassVar[int]
        ALWAYS_PRINT_PRIMITIVE_FIELDS_FIELD_NUMBER: _ClassVar[int]
        ALWAYS_PRINT_ENUMS_AS_INTS_FIELD_NUMBER: _ClassVar[int]
        PRESERVE_PROTO_FIELD_NAMES_FIELD_NUMBER: _ClassVar[int]
        STREAM_NEWLINE_DELIMITED_FIELD_NUMBER: _ClassVar[int]
        STREAM_SSE_STYLE_DELIMITED_FIELD_NUMBER: _ClassVar[int]
        add_whitespace: bool
        always_print_primitive_fields: bool
        always_print_enums_as_ints: bool
        preserve_proto_field_names: bool
        stream_newline_delimited: bool
        stream_sse_style_delimited: bool
        def __init__(self, add_whitespace: bool = ..., always_print_primitive_fields: bool = ..., always_print_enums_as_ints: bool = ..., preserve_proto_field_names: bool = ..., stream_newline_delimited: bool = ..., stream_sse_style_delimited: bool = ...) -> None: ...
    class RequestValidationOptions(_message.Message):
        __slots__ = ("reject_unknown_method", "reject_unknown_query_parameters", "reject_binding_body_field_collisions")
        REJECT_UNKNOWN_METHOD_FIELD_NUMBER: _ClassVar[int]
        REJECT_UNKNOWN_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
        REJECT_BINDING_BODY_FIELD_COLLISIONS_FIELD_NUMBER: _ClassVar[int]
        reject_unknown_method: bool
        reject_unknown_query_parameters: bool
        reject_binding_body_field_collisions: bool
        def __init__(self, reject_unknown_method: bool = ..., reject_unknown_query_parameters: bool = ..., reject_binding_body_field_collisions: bool = ...) -> None: ...
    PROTO_DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    PROTO_DESCRIPTOR_BIN_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    PRINT_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    MATCH_INCOMING_REQUEST_ROUTE_FIELD_NUMBER: _ClassVar[int]
    IGNORED_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    AUTO_MAPPING_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNKNOWN_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    CONVERT_GRPC_STATUS_FIELD_NUMBER: _ClassVar[int]
    URL_UNESCAPE_SPEC_FIELD_NUMBER: _ClassVar[int]
    QUERY_PARAM_UNESCAPE_PLUS_FIELD_NUMBER: _ClassVar[int]
    MATCH_UNREGISTERED_CUSTOM_VERB_FIELD_NUMBER: _ClassVar[int]
    REQUEST_VALIDATION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CASE_INSENSITIVE_ENUM_PARSING_FIELD_NUMBER: _ClassVar[int]
    MAX_REQUEST_BODY_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_RESPONSE_BODY_SIZE_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_UNKNOWN_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    proto_descriptor: str
    proto_descriptor_bin: bytes
    services: _containers.RepeatedScalarFieldContainer[str]
    print_options: GrpcJsonTranscoder.PrintOptions
    match_incoming_request_route: bool
    ignored_query_parameters: _containers.RepeatedScalarFieldContainer[str]
    auto_mapping: bool
    ignore_unknown_query_parameters: bool
    convert_grpc_status: bool
    url_unescape_spec: GrpcJsonTranscoder.UrlUnescapeSpec
    query_param_unescape_plus: bool
    match_unregistered_custom_verb: bool
    request_validation_options: GrpcJsonTranscoder.RequestValidationOptions
    case_insensitive_enum_parsing: bool
    max_request_body_size: _wrappers_pb2.UInt32Value
    max_response_body_size: _wrappers_pb2.UInt32Value
    capture_unknown_query_parameters: bool
    def __init__(self, proto_descriptor: _Optional[str] = ..., proto_descriptor_bin: _Optional[bytes] = ..., services: _Optional[_Iterable[str]] = ..., print_options: _Optional[_Union[GrpcJsonTranscoder.PrintOptions, _Mapping]] = ..., match_incoming_request_route: bool = ..., ignored_query_parameters: _Optional[_Iterable[str]] = ..., auto_mapping: bool = ..., ignore_unknown_query_parameters: bool = ..., convert_grpc_status: bool = ..., url_unescape_spec: _Optional[_Union[GrpcJsonTranscoder.UrlUnescapeSpec, str]] = ..., query_param_unescape_plus: bool = ..., match_unregistered_custom_verb: bool = ..., request_validation_options: _Optional[_Union[GrpcJsonTranscoder.RequestValidationOptions, _Mapping]] = ..., case_insensitive_enum_parsing: bool = ..., max_request_body_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_response_body_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., capture_unknown_query_parameters: bool = ...) -> None: ...

class UnknownQueryParams(_message.Message):
    __slots__ = ("key",)
    class Values(_message.Message):
        __slots__ = ("values",)
        VALUES_FIELD_NUMBER: _ClassVar[int]
        values: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...
    class KeyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownQueryParams.Values
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownQueryParams.Values, _Mapping]] = ...) -> None: ...
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: _containers.MessageMap[str, UnknownQueryParams.Values]
    def __init__(self, key: _Optional[_Mapping[str, UnknownQueryParams.Values]] = ...) -> None: ...
