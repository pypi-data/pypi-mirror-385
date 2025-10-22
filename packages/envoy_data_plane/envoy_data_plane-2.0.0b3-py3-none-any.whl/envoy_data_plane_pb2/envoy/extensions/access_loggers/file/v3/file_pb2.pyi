from envoy.config.core.v3 import substitution_format_string_pb2 as _substitution_format_string_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileAccessLog(_message.Message):
    __slots__ = ("path", "format", "json_format", "typed_json_format", "log_format")
    PATH_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    JSON_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TYPED_JSON_FORMAT_FIELD_NUMBER: _ClassVar[int]
    LOG_FORMAT_FIELD_NUMBER: _ClassVar[int]
    path: str
    format: str
    json_format: _struct_pb2.Struct
    typed_json_format: _struct_pb2.Struct
    log_format: _substitution_format_string_pb2.SubstitutionFormatString
    def __init__(self, path: _Optional[str] = ..., format: _Optional[str] = ..., json_format: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_json_format: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., log_format: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ...) -> None: ...
