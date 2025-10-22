from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import substitution_format_string_pb2 as _substitution_format_string_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalResponsePolicy(_message.Message):
    __slots__ = ("body", "body_format", "status_code", "response_headers_to_add")
    BODY_FIELD_NUMBER: _ClassVar[int]
    BODY_FORMAT_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    body: _base_pb2.DataSource
    body_format: _substitution_format_string_pb2.SubstitutionFormatString
    status_code: _wrappers_pb2.UInt32Value
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    def __init__(self, body: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., body_format: _Optional[_Union[_substitution_format_string_pb2.SubstitutionFormatString, _Mapping]] = ..., status_code: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ...) -> None: ...
