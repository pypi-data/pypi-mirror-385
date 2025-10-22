from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Compressor(_message.Message):
    __slots__ = ("content_length", "content_type", "disable_on_etag_header", "remove_accept_encoding_header", "runtime_enabled")
    CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ON_ETAG_HEADER_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ACCEPT_ENCODING_HEADER_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    content_length: _wrappers_pb2.UInt32Value
    content_type: _containers.RepeatedScalarFieldContainer[str]
    disable_on_etag_header: bool
    remove_accept_encoding_header: bool
    runtime_enabled: _base_pb2.RuntimeFeatureFlag
    def __init__(self, content_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., content_type: _Optional[_Iterable[str]] = ..., disable_on_etag_header: bool = ..., remove_accept_encoding_header: bool = ..., runtime_enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ...) -> None: ...
