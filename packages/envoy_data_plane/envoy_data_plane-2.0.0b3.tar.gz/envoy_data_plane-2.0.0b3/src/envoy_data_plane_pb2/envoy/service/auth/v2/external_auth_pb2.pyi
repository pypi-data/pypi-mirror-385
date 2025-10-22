from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.service.auth.v2 import attribute_context_pb2 as _attribute_context_pb2
from envoy.type import http_status_pb2 as _http_status_pb2
from google.rpc import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckRequest(_message.Message):
    __slots__ = ("attributes",)
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    attributes: _attribute_context_pb2.AttributeContext
    def __init__(self, attributes: _Optional[_Union[_attribute_context_pb2.AttributeContext, _Mapping]] = ...) -> None: ...

class DeniedHttpResponse(_message.Message):
    __slots__ = ("status", "headers", "body")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    status: _http_status_pb2.HttpStatus
    headers: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    body: str
    def __init__(self, status: _Optional[_Union[_http_status_pb2.HttpStatus, _Mapping]] = ..., headers: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., body: _Optional[str] = ...) -> None: ...

class OkHttpResponse(_message.Message):
    __slots__ = ("headers",)
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    headers: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    def __init__(self, headers: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ...) -> None: ...

class CheckResponse(_message.Message):
    __slots__ = ("status", "denied_response", "ok_response")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DENIED_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    OK_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status: _status_pb2.Status
    denied_response: DeniedHttpResponse
    ok_response: OkHttpResponse
    def __init__(self, status: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., denied_response: _Optional[_Union[DeniedHttpResponse, _Mapping]] = ..., ok_response: _Optional[_Union[OkHttpResponse, _Mapping]] = ...) -> None: ...
