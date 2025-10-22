from envoy.extensions.transport_sockets.tls.v3 import common_pb2 as _common_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("san_matcher", "any_validated_client_certificate")
    SAN_MATCHER_FIELD_NUMBER: _ClassVar[int]
    ANY_VALIDATED_CLIENT_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    san_matcher: _common_pb2.SubjectAltNameMatcher
    any_validated_client_certificate: bool
    def __init__(self, san_matcher: _Optional[_Union[_common_pb2.SubjectAltNameMatcher, _Mapping]] = ..., any_validated_client_certificate: bool = ...) -> None: ...
