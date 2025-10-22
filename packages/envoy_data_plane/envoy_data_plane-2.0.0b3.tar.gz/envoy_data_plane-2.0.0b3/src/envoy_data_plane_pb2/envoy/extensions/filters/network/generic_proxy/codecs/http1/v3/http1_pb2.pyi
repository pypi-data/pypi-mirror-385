from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Http1CodecConfig(_message.Message):
    __slots__ = ("single_frame_mode", "max_buffer_size")
    SINGLE_FRAME_MODE_FIELD_NUMBER: _ClassVar[int]
    MAX_BUFFER_SIZE_FIELD_NUMBER: _ClassVar[int]
    single_frame_mode: _wrappers_pb2.BoolValue
    max_buffer_size: _wrappers_pb2.UInt32Value
    def __init__(self, single_frame_mode: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., max_buffer_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
