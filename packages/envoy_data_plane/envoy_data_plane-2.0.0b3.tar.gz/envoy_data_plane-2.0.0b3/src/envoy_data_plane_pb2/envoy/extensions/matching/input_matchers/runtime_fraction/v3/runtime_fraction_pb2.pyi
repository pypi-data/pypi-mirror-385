from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RuntimeFraction(_message.Message):
    __slots__ = ("runtime_fraction", "seed")
    RUNTIME_FRACTION_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    runtime_fraction: _base_pb2.RuntimeFractionalPercent
    seed: int
    def __init__(self, runtime_fraction: _Optional[_Union[_base_pb2.RuntimeFractionalPercent, _Mapping]] = ..., seed: _Optional[int] = ...) -> None: ...
