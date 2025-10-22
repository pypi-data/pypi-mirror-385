from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Cors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CorsPolicy(_message.Message):
    __slots__ = ("allow_origin_string_match", "allow_methods", "allow_headers", "expose_headers", "max_age", "allow_credentials", "filter_enabled", "shadow_enabled", "allow_private_network_access", "forward_not_matching_preflights")
    ALLOW_ORIGIN_STRING_MATCH_FIELD_NUMBER: _ClassVar[int]
    ALLOW_METHODS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_HEADERS_FIELD_NUMBER: _ClassVar[int]
    EXPOSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    MAX_AGE_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SHADOW_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PRIVATE_NETWORK_ACCESS_FIELD_NUMBER: _ClassVar[int]
    FORWARD_NOT_MATCHING_PREFLIGHTS_FIELD_NUMBER: _ClassVar[int]
    allow_origin_string_match: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    allow_methods: str
    allow_headers: str
    expose_headers: str
    max_age: str
    allow_credentials: _wrappers_pb2.BoolValue
    filter_enabled: _base_pb2.RuntimeFractionalPercent
    shadow_enabled: _base_pb2.RuntimeFractionalPercent
    allow_private_network_access: _wrappers_pb2.BoolValue
    forward_not_matching_preflights: _wrappers_pb2.BoolValue
    def __init__(self, allow_origin_string_match: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., allow_methods: _Optional[str] = ..., allow_headers: _Optional[str] = ..., expose_headers: _Optional[str] = ..., max_age: _Optional[str] = ..., allow_credentials: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., filter_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., shadow_enabled: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., allow_private_network_access: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., forward_not_matching_preflights: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
