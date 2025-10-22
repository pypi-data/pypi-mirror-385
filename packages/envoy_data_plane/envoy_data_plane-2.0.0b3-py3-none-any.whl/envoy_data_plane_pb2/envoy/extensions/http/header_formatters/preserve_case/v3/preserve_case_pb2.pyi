from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PreserveCaseFormatterConfig(_message.Message):
    __slots__ = ("forward_reason_phrase", "formatter_type_on_envoy_headers")
    class FormatterTypeOnEnvoyHeaders(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[PreserveCaseFormatterConfig.FormatterTypeOnEnvoyHeaders]
        PROPER_CASE: _ClassVar[PreserveCaseFormatterConfig.FormatterTypeOnEnvoyHeaders]
    DEFAULT: PreserveCaseFormatterConfig.FormatterTypeOnEnvoyHeaders
    PROPER_CASE: PreserveCaseFormatterConfig.FormatterTypeOnEnvoyHeaders
    FORWARD_REASON_PHRASE_FIELD_NUMBER: _ClassVar[int]
    FORMATTER_TYPE_ON_ENVOY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    forward_reason_phrase: bool
    formatter_type_on_envoy_headers: PreserveCaseFormatterConfig.FormatterTypeOnEnvoyHeaders
    def __init__(self, forward_reason_phrase: bool = ..., formatter_type_on_envoy_headers: _Optional[_Union[PreserveCaseFormatterConfig.FormatterTypeOnEnvoyHeaders, str]] = ...) -> None: ...
