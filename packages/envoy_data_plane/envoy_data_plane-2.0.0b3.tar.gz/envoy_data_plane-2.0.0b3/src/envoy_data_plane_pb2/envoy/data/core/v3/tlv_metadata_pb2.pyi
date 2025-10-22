from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TlvsMetadata(_message.Message):
    __slots__ = ("typed_metadata",)
    class TypedMetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    TYPED_METADATA_FIELD_NUMBER: _ClassVar[int]
    typed_metadata: _containers.ScalarMap[str, bytes]
    def __init__(self, typed_metadata: _Optional[_Mapping[str, bytes]] = ...) -> None: ...
