from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GrpcJsonTranscoder(_message.Message):
    __slots__ = ("proto_descriptor", "proto_descriptor_bin", "services", "print_options", "match_incoming_request_route", "ignored_query_parameters", "auto_mapping", "ignore_unknown_query_parameters", "convert_grpc_status")
    class PrintOptions(_message.Message):
        __slots__ = ("add_whitespace", "always_print_primitive_fields", "always_print_enums_as_ints", "preserve_proto_field_names")
        ADD_WHITESPACE_FIELD_NUMBER: _ClassVar[int]
        ALWAYS_PRINT_PRIMITIVE_FIELDS_FIELD_NUMBER: _ClassVar[int]
        ALWAYS_PRINT_ENUMS_AS_INTS_FIELD_NUMBER: _ClassVar[int]
        PRESERVE_PROTO_FIELD_NAMES_FIELD_NUMBER: _ClassVar[int]
        add_whitespace: bool
        always_print_primitive_fields: bool
        always_print_enums_as_ints: bool
        preserve_proto_field_names: bool
        def __init__(self, add_whitespace: bool = ..., always_print_primitive_fields: bool = ..., always_print_enums_as_ints: bool = ..., preserve_proto_field_names: bool = ...) -> None: ...
    PROTO_DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    PROTO_DESCRIPTOR_BIN_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    PRINT_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    MATCH_INCOMING_REQUEST_ROUTE_FIELD_NUMBER: _ClassVar[int]
    IGNORED_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    AUTO_MAPPING_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNKNOWN_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    CONVERT_GRPC_STATUS_FIELD_NUMBER: _ClassVar[int]
    proto_descriptor: str
    proto_descriptor_bin: bytes
    services: _containers.RepeatedScalarFieldContainer[str]
    print_options: GrpcJsonTranscoder.PrintOptions
    match_incoming_request_route: bool
    ignored_query_parameters: _containers.RepeatedScalarFieldContainer[str]
    auto_mapping: bool
    ignore_unknown_query_parameters: bool
    convert_grpc_status: bool
    def __init__(self, proto_descriptor: _Optional[str] = ..., proto_descriptor_bin: _Optional[bytes] = ..., services: _Optional[_Iterable[str]] = ..., print_options: _Optional[_Union[GrpcJsonTranscoder.PrintOptions, _Mapping]] = ..., match_incoming_request_route: bool = ..., ignored_query_parameters: _Optional[_Iterable[str]] = ..., auto_mapping: bool = ..., ignore_unknown_query_parameters: bool = ..., convert_grpc_status: bool = ...) -> None: ...
