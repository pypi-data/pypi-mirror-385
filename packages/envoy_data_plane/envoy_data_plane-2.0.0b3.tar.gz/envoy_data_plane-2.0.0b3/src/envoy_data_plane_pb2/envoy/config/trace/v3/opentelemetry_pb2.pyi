from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.config.core.v3 import http_service_pb2 as _http_service_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpenTelemetryConfig(_message.Message):
    __slots__ = ("grpc_service", "http_service", "service_name", "resource_detectors", "sampler", "max_cache_size")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_DETECTORS_FIELD_NUMBER: _ClassVar[int]
    SAMPLER_FIELD_NUMBER: _ClassVar[int]
    MAX_CACHE_SIZE_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    http_service: _http_service_pb2.HttpService
    service_name: str
    resource_detectors: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    sampler: _extension_pb2.TypedExtensionConfig
    max_cache_size: _wrappers_pb2.UInt32Value
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., http_service: _Optional[_Union[_http_service_pb2.HttpService, _Mapping]] = ..., service_name: _Optional[str] = ..., resource_detectors: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., sampler: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., max_cache_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
