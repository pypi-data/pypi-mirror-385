from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import udp_socket_config_pb2 as _udp_socket_config_pb2
from envoy.config.listener.v3 import quic_config_pb2 as _quic_config_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UdpListenerConfig(_message.Message):
    __slots__ = ("downstream_socket_config", "quic_options", "udp_packet_packet_writer_config")
    DOWNSTREAM_SOCKET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    QUIC_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    UDP_PACKET_PACKET_WRITER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    downstream_socket_config: _udp_socket_config_pb2.UdpSocketConfig
    quic_options: _quic_config_pb2.QuicProtocolOptions
    udp_packet_packet_writer_config: _extension_pb2.TypedExtensionConfig
    def __init__(self, downstream_socket_config: _Optional[_Union[_udp_socket_config_pb2.UdpSocketConfig, _Mapping]] = ..., quic_options: _Optional[_Union[_quic_config_pb2.QuicProtocolOptions, _Mapping]] = ..., udp_packet_packet_writer_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...

class ActiveRawUdpListenerConfig(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
