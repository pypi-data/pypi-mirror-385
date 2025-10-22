from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MappedAttributeBuilder(_message.Message):
    __slots__ = ("mapped_request_attributes",)
    class MappedRequestAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MAPPED_REQUEST_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    mapped_request_attributes: _containers.ScalarMap[str, str]
    def __init__(self, mapped_request_attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...
