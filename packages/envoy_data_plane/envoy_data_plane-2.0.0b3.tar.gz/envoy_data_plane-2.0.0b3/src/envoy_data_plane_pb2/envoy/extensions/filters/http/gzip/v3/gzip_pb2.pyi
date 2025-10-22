from envoy.extensions.filters.http.compressor.v3 import compressor_pb2 as _compressor_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Gzip(_message.Message):
    __slots__ = ("memory_level", "compression_level", "compression_strategy", "window_bits", "compressor", "chunk_size")
    class CompressionStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[Gzip.CompressionStrategy]
        FILTERED: _ClassVar[Gzip.CompressionStrategy]
        HUFFMAN: _ClassVar[Gzip.CompressionStrategy]
        RLE: _ClassVar[Gzip.CompressionStrategy]
    DEFAULT: Gzip.CompressionStrategy
    FILTERED: Gzip.CompressionStrategy
    HUFFMAN: Gzip.CompressionStrategy
    RLE: Gzip.CompressionStrategy
    class CompressionLevel(_message.Message):
        __slots__ = ()
        class Enum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DEFAULT: _ClassVar[Gzip.CompressionLevel.Enum]
            BEST: _ClassVar[Gzip.CompressionLevel.Enum]
            SPEED: _ClassVar[Gzip.CompressionLevel.Enum]
        DEFAULT: Gzip.CompressionLevel.Enum
        BEST: Gzip.CompressionLevel.Enum
        SPEED: Gzip.CompressionLevel.Enum
        def __init__(self) -> None: ...
    MEMORY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    WINDOW_BITS_FIELD_NUMBER: _ClassVar[int]
    COMPRESSOR_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    memory_level: _wrappers_pb2.UInt32Value
    compression_level: Gzip.CompressionLevel.Enum
    compression_strategy: Gzip.CompressionStrategy
    window_bits: _wrappers_pb2.UInt32Value
    compressor: _compressor_pb2.Compressor
    chunk_size: _wrappers_pb2.UInt32Value
    def __init__(self, memory_level: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., compression_level: _Optional[_Union[Gzip.CompressionLevel.Enum, str]] = ..., compression_strategy: _Optional[_Union[Gzip.CompressionStrategy, str]] = ..., window_bits: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., compressor: _Optional[_Union[_compressor_pb2.Compressor, _Mapping]] = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
