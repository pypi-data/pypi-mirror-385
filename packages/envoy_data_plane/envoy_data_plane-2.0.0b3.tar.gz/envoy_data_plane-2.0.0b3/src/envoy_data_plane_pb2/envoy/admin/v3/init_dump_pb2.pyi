from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnreadyTargetsDumps(_message.Message):
    __slots__ = ("unready_targets_dumps",)
    class UnreadyTargetsDump(_message.Message):
        __slots__ = ("name", "target_names")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TARGET_NAMES_FIELD_NUMBER: _ClassVar[int]
        name: str
        target_names: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, name: _Optional[str] = ..., target_names: _Optional[_Iterable[str]] = ...) -> None: ...
    UNREADY_TARGETS_DUMPS_FIELD_NUMBER: _ClassVar[int]
    unready_targets_dumps: _containers.RepeatedCompositeFieldContainer[UnreadyTargetsDumps.UnreadyTargetsDump]
    def __init__(self, unready_targets_dumps: _Optional[_Iterable[_Union[UnreadyTargetsDumps.UnreadyTargetsDump, _Mapping]]] = ...) -> None: ...
