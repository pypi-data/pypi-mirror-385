from envoy.extensions.transport_sockets.raw_buffer.v3 import raw_buffer_pb2 as _raw_buffer_pb2
from envoy.extensions.transport_sockets.tls.v3 import tls_pb2 as _tls_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StartTlsConfig(_message.Message):
    __slots__ = ("cleartext_socket_config", "tls_socket_config")
    CLEARTEXT_SOCKET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TLS_SOCKET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    cleartext_socket_config: _raw_buffer_pb2.RawBuffer
    tls_socket_config: _tls_pb2.DownstreamTlsContext
    def __init__(self, cleartext_socket_config: _Optional[_Union[_raw_buffer_pb2.RawBuffer, _Mapping]] = ..., tls_socket_config: _Optional[_Union[_tls_pb2.DownstreamTlsContext, _Mapping]] = ...) -> None: ...

class UpstreamStartTlsConfig(_message.Message):
    __slots__ = ("cleartext_socket_config", "tls_socket_config")
    CLEARTEXT_SOCKET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TLS_SOCKET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    cleartext_socket_config: _raw_buffer_pb2.RawBuffer
    tls_socket_config: _tls_pb2.UpstreamTlsContext
    def __init__(self, cleartext_socket_config: _Optional[_Union[_raw_buffer_pb2.RawBuffer, _Mapping]] = ..., tls_socket_config: _Optional[_Union[_tls_pb2.UpstreamTlsContext, _Mapping]] = ...) -> None: ...
