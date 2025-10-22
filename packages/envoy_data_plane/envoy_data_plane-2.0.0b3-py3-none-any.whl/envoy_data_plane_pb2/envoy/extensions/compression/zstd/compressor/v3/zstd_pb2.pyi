from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Zstd(_message.Message):
    __slots__ = ("compression_level", "enable_checksum", "strategy", "dictionary", "chunk_size")
    class Strategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[Zstd.Strategy]
        FAST: _ClassVar[Zstd.Strategy]
        DFAST: _ClassVar[Zstd.Strategy]
        GREEDY: _ClassVar[Zstd.Strategy]
        LAZY: _ClassVar[Zstd.Strategy]
        LAZY2: _ClassVar[Zstd.Strategy]
        BTLAZY2: _ClassVar[Zstd.Strategy]
        BTOPT: _ClassVar[Zstd.Strategy]
        BTULTRA: _ClassVar[Zstd.Strategy]
        BTULTRA2: _ClassVar[Zstd.Strategy]
    DEFAULT: Zstd.Strategy
    FAST: Zstd.Strategy
    DFAST: Zstd.Strategy
    GREEDY: Zstd.Strategy
    LAZY: Zstd.Strategy
    LAZY2: Zstd.Strategy
    BTLAZY2: Zstd.Strategy
    BTOPT: Zstd.Strategy
    BTULTRA: Zstd.Strategy
    BTULTRA2: Zstd.Strategy
    COMPRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    ENABLE_CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    DICTIONARY_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    compression_level: _wrappers_pb2.UInt32Value
    enable_checksum: bool
    strategy: Zstd.Strategy
    dictionary: _base_pb2.DataSource
    chunk_size: _wrappers_pb2.UInt32Value
    def __init__(self, compression_level: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enable_checksum: bool = ..., strategy: _Optional[_Union[Zstd.Strategy, str]] = ..., dictionary: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
