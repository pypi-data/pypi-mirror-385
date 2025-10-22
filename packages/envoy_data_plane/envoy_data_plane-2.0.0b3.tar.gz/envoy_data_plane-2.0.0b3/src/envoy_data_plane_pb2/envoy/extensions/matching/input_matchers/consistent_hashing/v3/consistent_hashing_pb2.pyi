from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ConsistentHashing(_message.Message):
    __slots__ = ("threshold", "modulo", "seed")
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    MODULO_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    threshold: int
    modulo: int
    seed: int
    def __init__(self, threshold: _Optional[int] = ..., modulo: _Optional[int] = ..., seed: _Optional[int] = ...) -> None: ...
