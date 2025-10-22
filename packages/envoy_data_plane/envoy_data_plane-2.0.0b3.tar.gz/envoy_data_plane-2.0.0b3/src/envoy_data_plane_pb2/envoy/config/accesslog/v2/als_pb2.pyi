import datetime

from envoy.api.v2.core import grpc_service_pb2 as _grpc_service_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpGrpcAccessLogConfig(_message.Message):
    __slots__ = ("common_config", "additional_request_headers_to_log", "additional_response_headers_to_log", "additional_response_trailers_to_log")
    COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_REQUEST_HEADERS_TO_LOG_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_RESPONSE_HEADERS_TO_LOG_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_RESPONSE_TRAILERS_TO_LOG_FIELD_NUMBER: _ClassVar[int]
    common_config: CommonGrpcAccessLogConfig
    additional_request_headers_to_log: _containers.RepeatedScalarFieldContainer[str]
    additional_response_headers_to_log: _containers.RepeatedScalarFieldContainer[str]
    additional_response_trailers_to_log: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, common_config: _Optional[_Union[CommonGrpcAccessLogConfig, _Mapping]] = ..., additional_request_headers_to_log: _Optional[_Iterable[str]] = ..., additional_response_headers_to_log: _Optional[_Iterable[str]] = ..., additional_response_trailers_to_log: _Optional[_Iterable[str]] = ...) -> None: ...

class TcpGrpcAccessLogConfig(_message.Message):
    __slots__ = ("common_config",)
    COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
    common_config: CommonGrpcAccessLogConfig
    def __init__(self, common_config: _Optional[_Union[CommonGrpcAccessLogConfig, _Mapping]] = ...) -> None: ...

class CommonGrpcAccessLogConfig(_message.Message):
    __slots__ = ("log_name", "grpc_service", "buffer_flush_interval", "buffer_size_bytes", "filter_state_objects_to_log")
    LOG_NAME_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BUFFER_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATE_OBJECTS_TO_LOG_FIELD_NUMBER: _ClassVar[int]
    log_name: str
    grpc_service: _grpc_service_pb2.GrpcService
    buffer_flush_interval: _duration_pb2.Duration
    buffer_size_bytes: _wrappers_pb2.UInt32Value
    filter_state_objects_to_log: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, log_name: _Optional[str] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., buffer_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., buffer_size_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., filter_state_objects_to_log: _Optional[_Iterable[str]] = ...) -> None: ...
