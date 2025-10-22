from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Data(_message.Message):
    __slots__ = ("data", "end_of_stream")
    DATA_FIELD_NUMBER: _ClassVar[int]
    END_OF_STREAM_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    end_of_stream: bool
    def __init__(self, data: _Optional[bytes] = ..., end_of_stream: bool = ...) -> None: ...

class ProcessingRequest(_message.Message):
    __slots__ = ("read_data", "write_data", "metadata")
    READ_DATA_FIELD_NUMBER: _ClassVar[int]
    WRITE_DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    read_data: Data
    write_data: Data
    metadata: _base_pb2.Metadata
    def __init__(self, read_data: _Optional[_Union[Data, _Mapping]] = ..., write_data: _Optional[_Union[Data, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...

class ProcessingResponse(_message.Message):
    __slots__ = ("read_data", "write_data", "data_processing_status", "connection_status", "dynamic_metadata")
    class DataProcessedStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ProcessingResponse.DataProcessedStatus]
        UNMODIFIED: _ClassVar[ProcessingResponse.DataProcessedStatus]
        MODIFIED: _ClassVar[ProcessingResponse.DataProcessedStatus]
    UNKNOWN: ProcessingResponse.DataProcessedStatus
    UNMODIFIED: ProcessingResponse.DataProcessedStatus
    MODIFIED: ProcessingResponse.DataProcessedStatus
    class ConnectionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONTINUE: _ClassVar[ProcessingResponse.ConnectionStatus]
        CLOSE: _ClassVar[ProcessingResponse.ConnectionStatus]
        CLOSE_RST: _ClassVar[ProcessingResponse.ConnectionStatus]
    CONTINUE: ProcessingResponse.ConnectionStatus
    CLOSE: ProcessingResponse.ConnectionStatus
    CLOSE_RST: ProcessingResponse.ConnectionStatus
    READ_DATA_FIELD_NUMBER: _ClassVar[int]
    WRITE_DATA_FIELD_NUMBER: _ClassVar[int]
    DATA_PROCESSING_STATUS_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_STATUS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
    read_data: Data
    write_data: Data
    data_processing_status: ProcessingResponse.DataProcessedStatus
    connection_status: ProcessingResponse.ConnectionStatus
    dynamic_metadata: _struct_pb2.Struct
    def __init__(self, read_data: _Optional[_Union[Data, _Mapping]] = ..., write_data: _Optional[_Union[Data, _Mapping]] = ..., data_processing_status: _Optional[_Union[ProcessingResponse.DataProcessedStatus, str]] = ..., connection_status: _Optional[_Union[ProcessingResponse.ConnectionStatus, str]] = ..., dynamic_metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
