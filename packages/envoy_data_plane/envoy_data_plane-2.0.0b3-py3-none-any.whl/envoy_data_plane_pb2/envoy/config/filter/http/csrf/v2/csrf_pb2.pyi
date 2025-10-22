from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CsrfPolicy(_message.Message):
    __slots__ = ("filter_enabled", "shadow_enabled", "additional_origins")
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SHADOW_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_ORIGINS_FIELD_NUMBER: _ClassVar[int]
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    shadow_enabled: _base_pb2.RuntimeFractionalPercent
    additional_origins: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    def __init__(self, filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., shadow_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., additional_origins: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ...) -> None: ...
