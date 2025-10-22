from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.data.tap.v3 import wrapper_pb2 as _wrapper_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamTapsRequest(_message.Message):
    __slots__ = ("identifier", "trace_id", "trace")
    class Identifier(_message.Message):
        __slots__ = ("node", "tap_id")
        NODE_FIELD_NUMBER: _ClassVar[int]
        TAP_ID_FIELD_NUMBER: _ClassVar[int]
        node: _base_pb2.Node
        tap_id: str
        def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., tap_id: _Optional[str] = ...) -> None: ...
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    identifier: StreamTapsRequest.Identifier
    trace_id: int
    trace: _wrapper_pb2.TraceWrapper
    def __init__(self, identifier: _Optional[_Union[StreamTapsRequest.Identifier, _Mapping]] = ..., trace_id: _Optional[int] = ..., trace: _Optional[_Union[_wrapper_pb2.TraceWrapper, _Mapping]] = ...) -> None: ...

class StreamTapsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
