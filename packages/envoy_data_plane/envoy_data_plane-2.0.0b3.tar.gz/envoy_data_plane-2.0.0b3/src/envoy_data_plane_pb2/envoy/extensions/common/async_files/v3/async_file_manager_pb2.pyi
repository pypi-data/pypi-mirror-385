from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AsyncFileManagerConfig(_message.Message):
    __slots__ = ("id", "thread_pool")
    class ThreadPool(_message.Message):
        __slots__ = ("thread_count",)
        THREAD_COUNT_FIELD_NUMBER: _ClassVar[int]
        thread_count: int
        def __init__(self, thread_count: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_POOL_FIELD_NUMBER: _ClassVar[int]
    id: str
    thread_pool: AsyncFileManagerConfig.ThreadPool
    def __init__(self, id: _Optional[str] = ..., thread_pool: _Optional[_Union[AsyncFileManagerConfig.ThreadPool, _Mapping]] = ...) -> None: ...
