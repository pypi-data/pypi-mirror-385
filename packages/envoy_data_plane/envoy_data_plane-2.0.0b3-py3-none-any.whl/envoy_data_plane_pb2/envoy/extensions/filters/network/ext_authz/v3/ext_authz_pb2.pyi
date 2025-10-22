from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from envoy.type.matcher.v3 import metadata_pb2 as _metadata_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtAuthz(_message.Message):
    __slots__ = ("stat_prefix", "grpc_service", "failure_mode_allow", "include_peer_certificate", "transport_api_version", "filter_enabled_metadata", "bootstrap_metadata_labels_key", "include_tls_session", "send_tls_alert_on_denial")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MODE_ALLOW_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PEER_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    FILTER_ENABLED_METADATA_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_METADATA_LABELS_KEY_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_TLS_SESSION_FIELD_NUMBER: _ClassVar[int]
    SEND_TLS_ALERT_ON_DENIAL_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    grpc_service: _grpc_service_pb2.GrpcService
    failure_mode_allow: bool
    include_peer_certificate: bool
    transport_api_version: _config_source_pb2.ApiVersion
    filter_enabled_metadata: _metadata_pb2.MetadataMatcher
    bootstrap_metadata_labels_key: str
    include_tls_session: bool
    send_tls_alert_on_denial: bool
    def __init__(self, stat_prefix: _Optional[str] = ..., grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., failure_mode_allow: bool = ..., include_peer_certificate: bool = ..., transport_api_version: _Optional[_Union[_config_source_pb2.ApiVersion, str]] = ..., filter_enabled_metadata: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., bootstrap_metadata_labels_key: _Optional[str] = ..., include_tls_session: bool = ..., send_tls_alert_on_denial: bool = ...) -> None: ...
