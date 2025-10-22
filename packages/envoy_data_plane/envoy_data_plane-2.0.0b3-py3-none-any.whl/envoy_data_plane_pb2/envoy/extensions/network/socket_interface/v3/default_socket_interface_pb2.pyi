from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DefaultSocketInterface(_message.Message):
    __slots__ = ("io_uring_options",)
    IO_URING_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    io_uring_options: IoUringOptions
    def __init__(self, io_uring_options: _Optional[_Union[IoUringOptions, _Mapping]] = ...) -> None: ...

class IoUringOptions(_message.Message):
    __slots__ = ("io_uring_size", "enable_submission_queue_polling", "read_buffer_size", "write_timeout_ms")
    IO_URING_SIZE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_SUBMISSION_QUEUE_POLLING_FIELD_NUMBER: _ClassVar[int]
    READ_BUFFER_SIZE_FIELD_NUMBER: _ClassVar[int]
    WRITE_TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    io_uring_size: _wrappers_pb2.UInt32Value
    enable_submission_queue_polling: bool
    read_buffer_size: _wrappers_pb2.UInt32Value
    write_timeout_ms: _wrappers_pb2.UInt32Value
    def __init__(self, io_uring_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enable_submission_queue_polling: bool = ..., read_buffer_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., write_timeout_ms: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
