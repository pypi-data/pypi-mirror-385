from envoy.type.v3 import http_status_pb2 as _http_status_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CustomHeaderConfig(_message.Message):
    __slots__ = ("header_name", "allow_extension_to_set_address_as_trusted", "reject_with_status")
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    ALLOW_EXTENSION_TO_SET_ADDRESS_AS_TRUSTED_FIELD_NUMBER: _ClassVar[int]
    REJECT_WITH_STATUS_FIELD_NUMBER: _ClassVar[int]
    header_name: str
    allow_extension_to_set_address_as_trusted: bool
    reject_with_status: _http_status_pb2.HttpStatus
    def __init__(self, header_name: _Optional[str] = ..., allow_extension_to_set_address_as_trusted: bool = ..., reject_with_status: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ...) -> None: ...
