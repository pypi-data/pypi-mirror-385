from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class XRayConfig(_message.Message):
    __slots__ = ("daemon_endpoint", "segment_name", "sampling_rule_manifest")
    DAEMON_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLING_RULE_MANIFEST_FIELD_NUMBER: _ClassVar[int]
    daemon_endpoint: _address_pb2.SocketAddress
    segment_name: str
    sampling_rule_manifest: _base_pb2.DataSource
    def __init__(self, daemon_endpoint: _Optional[_Union[_address_pb2.SocketAddress, _Mapping]] = ..., segment_name: _Optional[str] = ..., sampling_rule_manifest: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
