from envoy.config.filter.http.compressor.v2 import compressor_pb2 as _compressor_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Gzip(_message.Message):
    __slots__ = ("memory_level", "content_length", "compression_level", "compression_strategy", "content_type", "disable_on_etag_header", "remove_accept_encoding_header", "window_bits", "compressor")
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
    CONTENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ON_ETAG_HEADER_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ACCEPT_ENCODING_HEADER_FIELD_NUMBER: _ClassVar[int]
    WINDOW_BITS_FIELD_NUMBER: _ClassVar[int]
    COMPRESSOR_FIELD_NUMBER: _ClassVar[int]
    memory_level: _wrappers_pb2.UInt32Value
    content_length: _wrappers_pb2.UInt32Value
    compression_level: Gzip.CompressionLevel.Enum
    compression_strategy: Gzip.CompressionStrategy
    content_type: _containers.RepeatedScalarFieldContainer[str]
    disable_on_etag_header: bool
    remove_accept_encoding_header: bool
    window_bits: _wrappers_pb2.UInt32Value
    compressor: _compressor_pb2.Compressor
    def __init__(self, memory_level: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., content_length: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., compression_level: _Optional[_Union[Gzip.CompressionLevel.Enum, str]] = ..., compression_strategy: _Optional[_Union[Gzip.CompressionStrategy, str]] = ..., content_type: _Optional[_Iterable[str]] = ..., disable_on_etag_header: bool = ..., remove_accept_encoding_header: bool = ..., window_bits: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., compressor: _Optional[_Union[_compressor_pb2.Compressor, _Mapping]] = ...) -> None: ...
