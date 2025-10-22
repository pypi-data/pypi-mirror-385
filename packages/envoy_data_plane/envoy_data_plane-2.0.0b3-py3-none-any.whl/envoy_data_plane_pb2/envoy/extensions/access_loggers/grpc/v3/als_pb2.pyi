import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.type.tracing.v3 import custom_tag_pb2 as _custom_tag_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
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
    __slots__ = ("log_name", "grpc_service", "transport_api_version", "buffer_flush_interval", "buffer_size_bytes", "filter_state_objects_to_log", "grpc_stream_retry_policy", "custom_tags")
    LOG_NAME_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FLUSH_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BUFFER_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATE_OBJECTS_TO_LOG_FIELD_NUMBER: _ClassVar[int]
    GRPC_STREAM_RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
    log_name: str
    grpc_service: _grpc_service_pb2.GrpcService
    transport_api_version: _config_source_pb2.ApiVersion
    buffer_flush_interval: _duration_pb2.Duration
    buffer_size_bytes: _wrappers_pb2.UInt32Value
    filter_state_objects_to_log: _containers.RepeatedScalarFieldContainer[str]
    grpc_stream_retry_policy: _base_pb2.RetryPolicy
    custom_tags: _containers.RepeatedCompositeFieldContainer[_custom_tag_pb2.CustomTag]
    def __init__(self, log_name: _Optional[str] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., transport_api_version: _Optional[_Union[_config_source_pb2.ApiVersion, str]] = ..., buffer_flush_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., buffer_size_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., filter_state_objects_to_log: _Optional[_Iterable[str]] = ..., grpc_stream_retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ..., custom_tags: _Optional[_Iterable[_Union[_custom_tag_pb2.CustomTag, _Mapping]]] = ...) -> None: ...
