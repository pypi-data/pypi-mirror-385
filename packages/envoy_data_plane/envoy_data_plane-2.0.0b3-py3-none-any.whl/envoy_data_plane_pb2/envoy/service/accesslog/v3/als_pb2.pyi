from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.data.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamAccessLogsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamAccessLogsMessage(_message.Message):
    __slots__ = ("identifier", "http_logs", "tcp_logs")
    class Identifier(_message.Message):
        __slots__ = ("node", "log_name")
        NODE_FIELD_NUMBER: _ClassVar[int]
        LOG_NAME_FIELD_NUMBER: _ClassVar[int]
        node: _base_pb2.Node
        log_name: str
        def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ..., log_name: _Optional[str] = ...) -> None: ...
    class HTTPAccessLogEntries(_message.Message):
        __slots__ = ("log_entry",)
        LOG_ENTRY_FIELD_NUMBER: _ClassVar[int]
        log_entry: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.HTTPAccessLogEntry]
        def __init__(self, log_entry: _Optional[_Iterable[_Union[_accesslog_pb2.HTTPAccessLogEntry, _Mapping]]] = ...) -> None: ...
    class TCPAccessLogEntries(_message.Message):
        __slots__ = ("log_entry",)
        LOG_ENTRY_FIELD_NUMBER: _ClassVar[int]
        log_entry: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.TCPAccessLogEntry]
        def __init__(self, log_entry: _Optional[_Iterable[_Union[_accesslog_pb2.TCPAccessLogEntry, _Mapping]]] = ...) -> None: ...
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    HTTP_LOGS_FIELD_NUMBER: _ClassVar[int]
    TCP_LOGS_FIELD_NUMBER: _ClassVar[int]
    identifier: StreamAccessLogsMessage.Identifier
    http_logs: StreamAccessLogsMessage.HTTPAccessLogEntries
    tcp_logs: StreamAccessLogsMessage.TCPAccessLogEntries
    def __init__(self, identifier: _Optional[_Union[StreamAccessLogsMessage.Identifier, _Mapping]] = ..., http_logs: _Optional[_Union[StreamAccessLogsMessage.HTTPAccessLogEntries, _Mapping]] = ..., tcp_logs: _Optional[_Union[StreamAccessLogsMessage.TCPAccessLogEntries, _Mapping]] = ...) -> None: ...
