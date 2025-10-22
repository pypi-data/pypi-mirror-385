from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
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

class RedirectPolicy(_message.Message):
    __slots__ = ("uri", "redirect_action", "status_code", "response_headers_to_add", "request_headers_to_add", "modify_request_headers_action")
    URI_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_ACTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    MODIFY_REQUEST_HEADERS_ACTION_FIELD_NUMBER: _ClassVar[int]
    uri: str
    redirect_action: _route_components_pb2.RedirectAction
    status_code: _wrappers_pb2.UInt32Value
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    modify_request_headers_action: _extension_pb2.TypedExtensionConfig
    def __init__(self, uri: _Optional[str] = ..., redirect_action: _Optional[_Union[_route_components_pb2.RedirectAction, _Mapping]] = ..., status_code: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., modify_request_headers_action: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
