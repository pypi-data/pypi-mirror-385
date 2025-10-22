from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Gzip(_message.Message):
    __slots__ = ("memory_level", "compression_level", "compression_strategy", "window_bits", "chunk_size")
    class CompressionStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT_STRATEGY: _ClassVar[Gzip.CompressionStrategy]
        FILTERED: _ClassVar[Gzip.CompressionStrategy]
        HUFFMAN_ONLY: _ClassVar[Gzip.CompressionStrategy]
        RLE: _ClassVar[Gzip.CompressionStrategy]
        FIXED: _ClassVar[Gzip.CompressionStrategy]
    DEFAULT_STRATEGY: Gzip.CompressionStrategy
    FILTERED: Gzip.CompressionStrategy
    HUFFMAN_ONLY: Gzip.CompressionStrategy
    RLE: Gzip.CompressionStrategy
    FIXED: Gzip.CompressionStrategy
    class CompressionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT_COMPRESSION: _ClassVar[Gzip.CompressionLevel]
        BEST_SPEED: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_1: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_2: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_3: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_4: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_5: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_6: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_7: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_8: _ClassVar[Gzip.CompressionLevel]
        COMPRESSION_LEVEL_9: _ClassVar[Gzip.CompressionLevel]
        BEST_COMPRESSION: _ClassVar[Gzip.CompressionLevel]
    DEFAULT_COMPRESSION: Gzip.CompressionLevel
    BEST_SPEED: Gzip.CompressionLevel
    COMPRESSION_LEVEL_1: Gzip.CompressionLevel
    COMPRESSION_LEVEL_2: Gzip.CompressionLevel
    COMPRESSION_LEVEL_3: Gzip.CompressionLevel
    COMPRESSION_LEVEL_4: Gzip.CompressionLevel
    COMPRESSION_LEVEL_5: Gzip.CompressionLevel
    COMPRESSION_LEVEL_6: Gzip.CompressionLevel
    COMPRESSION_LEVEL_7: Gzip.CompressionLevel
    COMPRESSION_LEVEL_8: Gzip.CompressionLevel
    COMPRESSION_LEVEL_9: Gzip.CompressionLevel
    BEST_COMPRESSION: Gzip.CompressionLevel
    MEMORY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    WINDOW_BITS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    memory_level: _wrappers_pb2.UInt32Value
    compression_level: Gzip.CompressionLevel
    compression_strategy: Gzip.CompressionStrategy
    window_bits: _wrappers_pb2.UInt32Value
    chunk_size: _wrappers_pb2.UInt32Value
    def __init__(self, memory_level: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., compression_level: _Optional[_Union[Gzip.CompressionLevel, str]] = ..., compression_strategy: _Optional[_Union[Gzip.CompressionStrategy, str]] = ..., window_bits: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
