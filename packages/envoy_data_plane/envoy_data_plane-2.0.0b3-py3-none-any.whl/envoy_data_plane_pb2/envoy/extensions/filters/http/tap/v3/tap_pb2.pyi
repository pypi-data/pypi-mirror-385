from envoy.extensions.common.tap.v3 import common_pb2 as _common_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tap(_message.Message):
    __slots__ = ("common_config", "record_headers_received_time", "record_downstream_connection", "record_upstream_connection")
    COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
    RECORD_HEADERS_RECEIVED_TIME_FIELD_NUMBER: _ClassVar[int]
    RECORD_DOWNSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    RECORD_UPSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    common_config: _common_pb2.CommonExtensionConfig
    record_headers_received_time: bool
    record_downstream_connection: bool
    record_upstream_connection: bool
    def __init__(self, common_config: _Optional[_Union[_common_pb2.CommonExtensionConfig, _Mapping]] = ..., record_headers_received_time: bool = ..., record_downstream_connection: bool = ..., record_upstream_connection: bool = ...) -> None: ...
