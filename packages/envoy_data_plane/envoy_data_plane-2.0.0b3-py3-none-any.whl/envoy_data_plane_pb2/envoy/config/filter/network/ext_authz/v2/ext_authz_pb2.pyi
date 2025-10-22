from envoy.api.v2.core import grpc_service_pb2 as _grpc_service_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtAuthz(_message.Message):
    __slots__ = ("stat_prefix", "grpc_service", "failure_mode_allow", "include_peer_certificate")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PEER_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    grpc_service: _grpc_service_pb2.GrpcService
    failure_mode_allow: bool
    include_peer_certificate: bool
    def __init__(self, stat_prefix: _Optional[str] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., failure_mode_allow: bool = ..., include_peer_certificate: bool = ...) -> None: ...
