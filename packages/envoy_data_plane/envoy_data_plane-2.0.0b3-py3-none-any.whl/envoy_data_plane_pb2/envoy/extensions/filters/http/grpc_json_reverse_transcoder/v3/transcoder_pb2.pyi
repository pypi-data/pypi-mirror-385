from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GrpcJsonReverseTranscoder(_message.Message):
    __slots__ = ("descriptor_path", "descriptor_binary", "max_request_body_size", "max_response_body_size", "api_version_header", "request_json_print_options")
    class PrintOptions(_message.Message):
        __slots__ = ("always_print_primitive_fields", "always_print_enums_as_ints", "use_canonical_field_names")
        ALWAYS_PRINT_PRIMITIVE_FIELDS_FIELD_NUMBER: _ClassVar[int]
        ALWAYS_PRINT_ENUMS_AS_INTS_FIELD_NUMBER: _ClassVar[int]
        USE_CANONICAL_FIELD_NAMES_FIELD_NUMBER: _ClassVar[int]
        always_print_primitive_fields: bool
        always_print_enums_as_ints: bool
        use_canonical_field_names: bool
        def __init__(self, always_print_primitive_fields: bool = ..., always_print_enums_as_ints: bool = ..., use_canonical_field_names: bool = ...) -> None: ...
    DESCRIPTOR_PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_BINARY_FIELD_NUMBER: _ClassVar[int]
    MAX_REQUEST_BODY_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_RESPONSE_BODY_SIZE_FIELD_NUMBER: _ClassVar[int]
    API_VERSION_HEADER_FIELD_NUMBER: _ClassVar[int]
    REQUEST_JSON_PRINT_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    descriptor_path: str
    descriptor_binary: bytes
    max_request_body_size: _wrappers_pb2.UInt32Value
    max_response_body_size: _wrappers_pb2.UInt32Value
    api_version_header: str
    request_json_print_options: GrpcJsonReverseTranscoder.PrintOptions
    def __init__(self, descriptor_path: _Optional[str] = ..., descriptor_binary: _Optional[bytes] = ..., max_request_body_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_response_body_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., api_version_header: _Optional[str] = ..., request_json_print_options: _Optional[_Union[GrpcJsonReverseTranscoder.PrintOptions, _Mapping]] = ...) -> None: ...
