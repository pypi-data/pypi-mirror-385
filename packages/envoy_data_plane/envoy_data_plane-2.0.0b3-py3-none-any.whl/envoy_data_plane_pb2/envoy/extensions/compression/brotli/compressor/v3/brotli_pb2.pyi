from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Brotli(_message.Message):
    __slots__ = ("quality", "encoder_mode", "window_bits", "input_block_bits", "chunk_size", "disable_literal_context_modeling")
    class EncoderMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[Brotli.EncoderMode]
        GENERIC: _ClassVar[Brotli.EncoderMode]
        TEXT: _ClassVar[Brotli.EncoderMode]
        FONT: _ClassVar[Brotli.EncoderMode]
    DEFAULT: Brotli.EncoderMode
    GENERIC: Brotli.EncoderMode
    TEXT: Brotli.EncoderMode
    FONT: Brotli.EncoderMode
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    ENCODER_MODE_FIELD_NUMBER: _ClassVar[int]
    WINDOW_BITS_FIELD_NUMBER: _ClassVar[int]
    INPUT_BLOCK_BITS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_LITERAL_CONTEXT_MODELING_FIELD_NUMBER: _ClassVar[int]
    quality: _wrappers_pb2.UInt32Value
    encoder_mode: Brotli.EncoderMode
    window_bits: _wrappers_pb2.UInt32Value
    input_block_bits: _wrappers_pb2.UInt32Value
    chunk_size: _wrappers_pb2.UInt32Value
    disable_literal_context_modeling: bool
    def __init__(self, quality: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., encoder_mode: _Optional[_Union[Brotli.EncoderMode, str]] = ..., window_bits: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., input_block_bits: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., chunk_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., disable_literal_context_modeling: bool = ...) -> None: ...
