from envoy.extensions.filters.common.set_filter_state.v3 import value_pb2 as _value_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("on_request_headers",)
    ON_REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    on_request_headers: _containers.RepeatedCompositeFieldContainer[_value_pb2.FilterStateValue]
    def __init__(self, on_request_headers: _Optional[_Iterable[_Union[_value_pb2.FilterStateValue, _Mapping]]] = ...) -> None: ...
