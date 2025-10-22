from envoy.config.core.v3 import base_pb2 as _base_pb2
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
    __slots__ = ("common_config", "transport_socket", "socket_tap_config")
    COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
    SOCKET_TAP_CONFIG_FIELD_NUMBER: _ClassVar[int]
    common_config: _common_pb2.CommonExtensionConfig
    transport_socket: _base_pb2.TransportSocket
    socket_tap_config: SocketTapConfig
    def __init__(self, common_config: _Optional[_Union[_common_pb2.CommonExtensionConfig, _Mapping]] = ..., transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ..., socket_tap_config: _Optional[_Union[SocketTapConfig, _Mapping]] = ...) -> None: ...

class SocketTapConfig(_message.Message):
    __slots__ = ("set_connection_per_event", "stats_prefix")
    SET_CONNECTION_PER_EVENT_FIELD_NUMBER: _ClassVar[int]
    STATS_PREFIX_FIELD_NUMBER: _ClassVar[int]
    set_connection_per_event: bool
    stats_prefix: str
    def __init__(self, set_connection_per_event: bool = ..., stats_prefix: _Optional[str] = ...) -> None: ...
