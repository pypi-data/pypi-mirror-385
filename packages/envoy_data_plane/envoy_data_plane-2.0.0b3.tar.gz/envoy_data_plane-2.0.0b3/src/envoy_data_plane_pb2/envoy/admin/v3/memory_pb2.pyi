from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Memory(_message.Message):
    __slots__ = ("allocated", "heap_size", "pageheap_unmapped", "pageheap_free", "total_thread_cache", "total_physical_bytes")
    ALLOCATED_FIELD_NUMBER: _ClassVar[int]
    HEAP_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGEHEAP_UNMAPPED_FIELD_NUMBER: _ClassVar[int]
    PAGEHEAP_FREE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_THREAD_CACHE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PHYSICAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    allocated: int
    heap_size: int
    pageheap_unmapped: int
    pageheap_free: int
    total_thread_cache: int
    total_physical_bytes: int
    def __init__(self, allocated: _Optional[int] = ..., heap_size: _Optional[int] = ..., pageheap_unmapped: _Optional[int] = ..., pageheap_free: _Optional[int] = ..., total_thread_cache: _Optional[int] = ..., total_physical_bytes: _Optional[int] = ...) -> None: ...
