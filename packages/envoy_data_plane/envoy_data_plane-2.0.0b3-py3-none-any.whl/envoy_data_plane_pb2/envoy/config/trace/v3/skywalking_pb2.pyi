from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SkyWalkingConfig(_message.Message):
    __slots__ = ("grpc_service", "client_config")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    client_config: ClientConfig
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., client_config: _Optional[_Union[ClientConfig, _Mapping]] = ...) -> None: ...

class ClientConfig(_message.Message):
    __slots__ = ("service_name", "instance_name", "backend_token", "max_cache_size")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    BACKEND_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MAX_CACHE_SIZE_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    instance_name: str
    backend_token: str
    max_cache_size: _wrappers_pb2.UInt32Value
    def __init__(self, service_name: _Optional[str] = ..., instance_name: _Optional[str] = ..., backend_token: _Optional[str] = ..., max_cache_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
