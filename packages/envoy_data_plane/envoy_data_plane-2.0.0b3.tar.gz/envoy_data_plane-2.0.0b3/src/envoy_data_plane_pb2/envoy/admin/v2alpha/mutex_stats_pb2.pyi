from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MutexStats(_message.Message):
    __slots__ = ("num_contentions", "current_wait_cycles", "lifetime_wait_cycles")
    NUM_CONTENTIONS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_WAIT_CYCLES_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_WAIT_CYCLES_FIELD_NUMBER: _ClassVar[int]
    num_contentions: int
    current_wait_cycles: int
    lifetime_wait_cycles: int
    def __init__(self, num_contentions: _Optional[int] = ..., current_wait_cycles: _Optional[int] = ..., lifetime_wait_cycles: _Optional[int] = ...) -> None: ...
