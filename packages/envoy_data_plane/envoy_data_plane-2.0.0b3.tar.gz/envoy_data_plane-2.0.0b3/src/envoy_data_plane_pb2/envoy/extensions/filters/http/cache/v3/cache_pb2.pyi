from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CacheConfig(_message.Message):
    __slots__ = ("typed_config", "disabled", "allowed_vary_headers", "key_creator_params", "max_body_bytes", "ignore_request_cache_control_header")
    class KeyCreatorParams(_message.Message):
        __slots__ = ("exclude_scheme", "exclude_host", "query_parameters_included", "query_parameters_excluded")
        EXCLUDE_SCHEME_FIELD_NUMBER: _ClassVar[int]
        EXCLUDE_HOST_FIELD_NUMBER: _ClassVar[int]
        QUERY_PARAMETERS_INCLUDED_FIELD_NUMBER: _ClassVar[int]
        QUERY_PARAMETERS_EXCLUDED_FIELD_NUMBER: _ClassVar[int]
        exclude_scheme: bool
        exclude_host: bool
        query_parameters_included: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.QueryParameterMatcher]
        query_parameters_excluded: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.QueryParameterMatcher]
        def __init__(self, exclude_scheme: bool = ..., exclude_host: bool = ..., query_parameters_included: _Optional[_Iterable[_Union[_route_components_pb2.QueryParameterMatcher, _Mapping]]] = ..., query_parameters_excluded: _Optional[_Iterable[_Union[_route_components_pb2.QueryParameterMatcher, _Mapping]]] = ...) -> None: ...
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_VARY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    KEY_CREATOR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MAX_BODY_BYTES_FIELD_NUMBER: _ClassVar[int]
    IGNORE_REQUEST_CACHE_CONTROL_HEADER_FIELD_NUMBER: _ClassVar[int]
    typed_config: _any_pb2.Any
    disabled: _wrappers_pb2.BoolValue
    allowed_vary_headers: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    key_creator_params: CacheConfig.KeyCreatorParams
    max_body_bytes: int
    ignore_request_cache_control_header: bool
    def __init__(self, typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., disabled: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., allowed_vary_headers: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., key_creator_params: _Optional[_Union[CacheConfig.KeyCreatorParams, _Mapping]] = ..., max_body_bytes: _Optional[int] = ..., ignore_request_cache_control_header: bool = ...) -> None: ...
