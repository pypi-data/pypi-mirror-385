import datetime

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

class SocketEvent(_message.Message):
    __slots__ = ("timestamp", "read", "write", "closed", "connection")
    class Read(_message.Message):
        __slots__ = ("data",)
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _common_pb2.Body
        def __init__(self, data: _Optional[_Union[_common_pb2.Body, _Mapping]] = ...) -> None: ...
    class Write(_message.Message):
        __slots__ = ("data", "end_stream")
        DATA_FIELD_NUMBER: _ClassVar[int]
        END_STREAM_FIELD_NUMBER: _ClassVar[int]
        data: _common_pb2.Body
        end_stream: bool
        def __init__(self, data: _Optional[_Union[_common_pb2.Body, _Mapping]] = ..., end_stream: bool = ...) -> None: ...
    class Closed(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    READ_FIELD_NUMBER: _ClassVar[int]
    WRITE_FIELD_NUMBER: _ClassVar[int]
    CLOSED_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    read: SocketEvent.Read
    write: SocketEvent.Write
    closed: SocketEvent.Closed
    connection: _common_pb2.Connection
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., read: _Optional[_Union[SocketEvent.Read, _Mapping]] = ..., write: _Optional[_Union[SocketEvent.Write, _Mapping]] = ..., closed: _Optional[_Union[SocketEvent.Closed, _Mapping]] = ..., connection: _Optional[_Union[_common_pb2.Connection, _Mapping]] = ...) -> None: ...

class SocketBufferedTrace(_message.Message):
    __slots__ = ("trace_id", "connection", "events", "read_truncated", "write_truncated")
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    READ_TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    WRITE_TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    trace_id: int
    connection: _common_pb2.Connection
    events: _containers.RepeatedCompositeFieldContainer[SocketEvent]
    read_truncated: bool
    write_truncated: bool
    def __init__(self, trace_id: _Optional[int] = ..., connection: _Optional[_Union[_common_pb2.Connection, _Mapping]] = ..., events: _Optional[_Iterable[_Union[SocketEvent, _Mapping]]] = ..., read_truncated: bool = ..., write_truncated: bool = ...) -> None: ...

class SocketEvents(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[SocketEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[SocketEvent, _Mapping]]] = ...) -> None: ...

class SocketStreamedTraceSegment(_message.Message):
    __slots__ = ("trace_id", "connection", "event", "events")
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    trace_id: int
    connection: _common_pb2.Connection
    event: SocketEvent
    events: SocketEvents
    def __init__(self, trace_id: _Optional[int] = ..., connection: _Optional[_Union[_common_pb2.Connection, _Mapping]] = ..., event: _Optional[_Union[SocketEvent, _Mapping]] = ..., events: _Optional[_Union[SocketEvents, _Mapping]] = ...) -> None: ...
