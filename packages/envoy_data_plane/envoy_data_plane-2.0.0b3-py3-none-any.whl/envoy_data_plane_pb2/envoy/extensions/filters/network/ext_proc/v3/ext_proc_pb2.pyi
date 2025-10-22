import datetime

from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NetworkExternalProcessor(_message.Message):
    __slots__ = ("grpc_service", "failure_mode_allow", "processing_mode", "message_timeout", "stat_prefix", "metadata_options")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_MODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    METADATA_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    failure_mode_allow: bool
    processing_mode: ProcessingMode
    message_timeout: _duration_pb2.Duration
    stat_prefix: str
    metadata_options: MetadataOptions
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., failure_mode_allow: bool = ..., processing_mode: _Optional[_Union[ProcessingMode, _Mapping]] = ..., message_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., metadata_options: _Optional[_Union[MetadataOptions, _Mapping]] = ...) -> None: ...

class ProcessingMode(_message.Message):
    __slots__ = ("process_read", "process_write")
    class DataSendMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STREAMED: _ClassVar[ProcessingMode.DataSendMode]
        SKIP: _ClassVar[ProcessingMode.DataSendMode]
    STREAMED: ProcessingMode.DataSendMode
    SKIP: ProcessingMode.DataSendMode
    PROCESS_READ_FIELD_NUMBER: _ClassVar[int]
    PROCESS_WRITE_FIELD_NUMBER: _ClassVar[int]
    process_read: ProcessingMode.DataSendMode
    process_write: ProcessingMode.DataSendMode
    def __init__(self, process_read: _Optional[_Union[ProcessingMode.DataSendMode, str]] = ..., process_write: _Optional[_Union[ProcessingMode.DataSendMode, str]] = ...) -> None: ...

class MetadataOptions(_message.Message):
    __slots__ = ("forwarding_namespaces",)
    class MetadataNamespaces(_message.Message):
        __slots__ = ("untyped", "typed")
        UNTYPED_FIELD_NUMBER: _ClassVar[int]
        TYPED_FIELD_NUMBER: _ClassVar[int]
        untyped: _containers.RepeatedScalarFieldContainer[str]
        typed: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, untyped: _Optional[_Iterable[str]] = ..., typed: _Optional[_Iterable[str]] = ...) -> None: ...
    FORWARDING_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    forwarding_namespaces: MetadataOptions.MetadataNamespaces
    def __init__(self, forwarding_namespaces: _Optional[_Union[MetadataOptions.MetadataNamespaces, _Mapping]] = ...) -> None: ...
