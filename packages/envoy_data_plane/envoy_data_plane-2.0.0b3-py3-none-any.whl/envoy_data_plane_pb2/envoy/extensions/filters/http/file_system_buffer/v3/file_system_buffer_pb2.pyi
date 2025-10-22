from envoy.extensions.common.async_files.v3 import async_file_manager_pb2 as _async_file_manager_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BufferBehavior(_message.Message):
    __slots__ = ("stream_when_possible", "bypass", "inject_content_length_if_necessary", "fully_buffer_and_always_inject_content_length", "fully_buffer")
    class StreamWhenPossible(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Bypass(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class InjectContentLengthIfNecessary(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class FullyBufferAndAlwaysInjectContentLength(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class FullyBuffer(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    STREAM_WHEN_POSSIBLE_FIELD_NUMBER: _ClassVar[int]
    BYPASS_FIELD_NUMBER: _ClassVar[int]
    INJECT_CONTENT_LENGTH_IF_NECESSARY_FIELD_NUMBER: _ClassVar[int]
    FULLY_BUFFER_AND_ALWAYS_INJECT_CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    FULLY_BUFFER_FIELD_NUMBER: _ClassVar[int]
    stream_when_possible: BufferBehavior.StreamWhenPossible
    bypass: BufferBehavior.Bypass
    inject_content_length_if_necessary: BufferBehavior.InjectContentLengthIfNecessary
    fully_buffer_and_always_inject_content_length: BufferBehavior.FullyBufferAndAlwaysInjectContentLength
    fully_buffer: BufferBehavior.FullyBuffer
    def __init__(self, stream_when_possible: _Optional[_Union[BufferBehavior.StreamWhenPossible, _Mapping]] = ..., bypass: _Optional[_Union[BufferBehavior.Bypass, _Mapping]] = ..., inject_content_length_if_necessary: _Optional[_Union[BufferBehavior.InjectContentLengthIfNecessary, _Mapping]] = ..., fully_buffer_and_always_inject_content_length: _Optional[_Union[BufferBehavior.FullyBufferAndAlwaysInjectContentLength, _Mapping]] = ..., fully_buffer: _Optional[_Union[BufferBehavior.FullyBuffer, _Mapping]] = ...) -> None: ...

class StreamConfig(_message.Message):
    __slots__ = ("behavior", "memory_buffer_bytes_limit", "storage_buffer_bytes_limit", "storage_buffer_queue_high_watermark_bytes")
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BUFFER_BYTES_LIMIT_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUFFER_BYTES_LIMIT_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUFFER_QUEUE_HIGH_WATERMARK_BYTES_FIELD_NUMBER: _ClassVar[int]
    behavior: BufferBehavior
    memory_buffer_bytes_limit: _wrappers_pb2.UInt64Value
    storage_buffer_bytes_limit: _wrappers_pb2.UInt64Value
    storage_buffer_queue_high_watermark_bytes: _wrappers_pb2.UInt64Value
    def __init__(self, behavior: _Optional[_Union[BufferBehavior, _Mapping]] = ..., memory_buffer_bytes_limit: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., storage_buffer_bytes_limit: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., storage_buffer_queue_high_watermark_bytes: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...

class FileSystemBufferFilterConfig(_message.Message):
    __slots__ = ("manager_config", "storage_buffer_path", "request", "response")
    MANAGER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BUFFER_PATH_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    manager_config: _async_file_manager_pb2.AsyncFileManagerConfig
    storage_buffer_path: _wrappers_pb2.StringValue
    request: StreamConfig
    response: StreamConfig
    def __init__(self, manager_config: _Optional[_Union[_async_file_manager_pb2.AsyncFileManagerConfig, _Mapping]] = ..., storage_buffer_path: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., request: _Optional[_Union[StreamConfig, _Mapping]] = ..., response: _Optional[_Union[StreamConfig, _Mapping]] = ...) -> None: ...
