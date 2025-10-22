import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.data.tap.v3 import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpBufferedTrace(_message.Message):
    __slots__ = ("request", "response", "downstream_connection", "upstream_connection")
    class Message(_message.Message):
        __slots__ = ("headers", "body", "trailers", "headers_received_time")
        HEADERS_FIELD_NUMBER: _ClassVar[int]
        BODY_FIELD_NUMBER: _ClassVar[int]
        TRAILERS_FIELD_NUMBER: _ClassVar[int]
        HEADERS_RECEIVED_TIME_FIELD_NUMBER: _ClassVar[int]
        headers: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
        body: _common_pb2.Body
        trailers: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValue]
        headers_received_time: _timestamp_pb2.Timestamp
        def __init__(self, headers: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ..., body: _Optional[_Union[_common_pb2.Body, _Mapping]] = ..., trailers: _Optional[_Iterable[_Union[_base_pb2.HeaderValue, _Mapping]]] = ..., headers_received_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    request: HttpBufferedTrace.Message
    response: HttpBufferedTrace.Message
    downstream_connection: _common_pb2.Connection
    upstream_connection: _common_pb2.Connection
    def __init__(self, request: _Optional[_Union[HttpBufferedTrace.Message, _Mapping]] = ..., response: _Optional[_Union[HttpBufferedTrace.Message, _Mapping]] = ..., downstream_connection: _Optional[_Union[_common_pb2.Connection, _Mapping]] = ..., upstream_connection: _Optional[_Union[_common_pb2.Connection, _Mapping]] = ...) -> None: ...

class HttpStreamedTraceSegment(_message.Message):
    __slots__ = ("trace_id", "request_headers", "request_body_chunk", "request_trailers", "response_headers", "response_body_chunk", "response_trailers")
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_BODY_CHUNK_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_BODY_CHUNK_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    trace_id: int
    request_headers: _base_pb2.HeaderMap
    request_body_chunk: _common_pb2.Body
    request_trailers: _base_pb2.HeaderMap
    response_headers: _base_pb2.HeaderMap
    response_body_chunk: _common_pb2.Body
    response_trailers: _base_pb2.HeaderMap
    def __init__(self, trace_id: _Optional[int] = ..., request_headers: _Optional[_Union[_base_pb2.HeaderMap, _Mapping]] = ..., request_body_chunk: _Optional[_Union[_common_pb2.Body, _Mapping]] = ..., request_trailers: _Optional[_Union[_base_pb2.HeaderMap, _Mapping]] = ..., response_headers: _Optional[_Union[_base_pb2.HeaderMap, _Mapping]] = ..., response_body_chunk: _Optional[_Union[_common_pb2.Body, _Mapping]] = ..., response_trailers: _Optional[_Union[_base_pb2.HeaderMap, _Mapping]] = ...) -> None: ...
