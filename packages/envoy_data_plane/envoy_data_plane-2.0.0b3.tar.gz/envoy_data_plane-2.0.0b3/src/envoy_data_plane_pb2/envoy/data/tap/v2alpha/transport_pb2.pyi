import datetime

from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.data.tap.v2alpha import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Connection(_message.Message):
    __slots__ = ("local_address", "remote_address")
    LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    local_address: _address_pb2.Address
    remote_address: _address_pb2.Address
    def __init__(self, local_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., remote_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ...) -> None: ...

class SocketEvent(_message.Message):
    __slots__ = ("timestamp", "read", "write", "closed")
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
    timestamp: _timestamp_pb2.Timestamp
    read: SocketEvent.Read
    write: SocketEvent.Write
    closed: SocketEvent.Closed
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., read: _Optional[_Union[SocketEvent.Read, _Mapping]] = ..., write: _Optional[_Union[SocketEvent.Write, _Mapping]] = ..., closed: _Optional[_Union[SocketEvent.Closed, _Mapping]] = ...) -> None: ...

class SocketBufferedTrace(_message.Message):
    __slots__ = ("trace_id", "connection", "events", "read_truncated", "write_truncated")
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    READ_TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    WRITE_TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    trace_id: int
    connection: Connection
    events: _containers.RepeatedCompositeFieldContainer[SocketEvent]
    read_truncated: bool
    write_truncated: bool
    def __init__(self, trace_id: _Optional[int] = ..., connection: _Optional[_Union[Connection, _Mapping]] = ..., events: _Optional[_Iterable[_Union[SocketEvent, _Mapping]]] = ..., read_truncated: bool = ..., write_truncated: bool = ...) -> None: ...

class SocketStreamedTraceSegment(_message.Message):
    __slots__ = ("trace_id", "connection", "event")
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    trace_id: int
    connection: Connection
    event: SocketEvent
    def __init__(self, trace_id: _Optional[int] = ..., connection: _Optional[_Union[Connection, _Mapping]] = ..., event: _Optional[_Union[SocketEvent, _Mapping]] = ...) -> None: ...
