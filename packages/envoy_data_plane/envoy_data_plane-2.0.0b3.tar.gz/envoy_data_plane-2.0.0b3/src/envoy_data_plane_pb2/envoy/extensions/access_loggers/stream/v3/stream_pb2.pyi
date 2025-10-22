from envoy.config.core.v3 import substitution_format_string_pb2 as _substitution_format_string_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StdoutAccessLog(_message.Message):
    __slots__ = ("log_format",)
    LOG_FORMAT_FIELD_NUMBER: _ClassVar[int]
    log_format: _substitution_format_string_pb2.SubstitutionFormatString
    def __init__(self, log_format: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ...) -> None: ...

class StderrAccessLog(_message.Message):
    __slots__ = ("log_format",)
    LOG_FORMAT_FIELD_NUMBER: _ClassVar[int]
    log_format: _substitution_format_string_pb2.SubstitutionFormatString
    def __init__(self, log_format: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ...) -> None: ...
