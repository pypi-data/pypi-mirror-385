import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Validation(_message.Message):
    __slots__ = ("node_id_format", "cluster_id_format", "emit_dynamic_metadata", "dynamic_metadata_namespace")
    NODE_ID_FORMAT_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FORMAT_FIELD_NUMBER: _ClassVar[int]
    EMIT_DYNAMIC_METADATA_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    node_id_format: str
    cluster_id_format: str
    emit_dynamic_metadata: bool
    dynamic_metadata_namespace: str
    def __init__(self, node_id_format: _Optional[str] = ..., cluster_id_format: _Optional[str] = ..., emit_dynamic_metadata: bool = ..., dynamic_metadata_namespace: _Optional[str] = ...) -> None: ...

class ReverseTunnel(_message.Message):
    __slots__ = ("ping_interval", "auto_close_connections", "request_path", "request_method", "validation")
    PING_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    AUTO_CLOSE_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_PATH_FIELD_NUMBER: _ClassVar[int]
    REQUEST_METHOD_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_FIELD_NUMBER: _ClassVar[int]
    ping_interval: _duration_pb2.Duration
    auto_close_connections: bool
    request_path: str
    request_method: _base_pb2.RequestMethod
    validation: Validation
    def __init__(self, ping_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., auto_close_connections: bool = ..., request_path: _Optional[str] = ..., request_method: _Optional[_Union[_base_pb2.RequestMethod, str]] = ..., validation: _Optional[_Union[Validation, _Mapping]] = ...) -> None: ...
