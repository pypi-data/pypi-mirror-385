from envoy.data.tap.v3 import http_pb2 as _http_pb2
from envoy.data.tap.v3 import transport_pb2 as _transport_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TraceWrapper(_message.Message):
    __slots__ = ("http_buffered_trace", "http_streamed_trace_segment", "socket_buffered_trace", "socket_streamed_trace_segment")
    HTTP_BUFFERED_TRACE_FIELD_NUMBER: _ClassVar[int]
    HTTP_STREAMED_TRACE_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    SOCKET_BUFFERED_TRACE_FIELD_NUMBER: _ClassVar[int]
    SOCKET_STREAMED_TRACE_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    http_buffered_trace: _http_pb2.HttpBufferedTrace
    http_streamed_trace_segment: _http_pb2.HttpStreamedTraceSegment
    socket_buffered_trace: _transport_pb2.SocketBufferedTrace
    socket_streamed_trace_segment: _transport_pb2.SocketStreamedTraceSegment
    def __init__(self, http_buffered_trace: _Optional[_Union[_http_pb2.HttpBufferedTrace, _Mapping]] = ..., http_streamed_trace_segment: _Optional[_Union[_http_pb2.HttpStreamedTraceSegment, _Mapping]] = ..., socket_buffered_trace: _Optional[_Union[_transport_pb2.SocketBufferedTrace, _Mapping]] = ..., socket_streamed_trace_segment: _Optional[_Union[_transport_pb2.SocketStreamedTraceSegment, _Mapping]] = ...) -> None: ...
