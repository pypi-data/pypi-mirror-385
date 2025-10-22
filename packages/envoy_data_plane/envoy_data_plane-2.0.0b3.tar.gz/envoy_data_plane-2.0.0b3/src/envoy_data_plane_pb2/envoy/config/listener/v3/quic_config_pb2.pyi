import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import protocol_pb2 as _protocol_pb2
from envoy.config.core.v3 import socket_cmsg_headers_pb2 as _socket_cmsg_headers_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuicProtocolOptions(_message.Message):
    __slots__ = ("quic_protocol_options", "idle_timeout", "crypto_handshake_timeout", "enabled", "packets_to_read_to_connection_count_ratio", "crypto_stream_config", "proof_source_config", "connection_id_generator_config", "server_preferred_address_config", "send_disable_active_migration", "connection_debug_visitor_config", "save_cmsg_config", "reject_new_connections")
    QUIC_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    CRYPTO_HANDSHAKE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PACKETS_TO_READ_TO_CONNECTION_COUNT_RATIO_FIELD_NUMBER: _ClassVar[int]
    CRYPTO_STREAM_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROOF_SOURCE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_GENERATOR_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SERVER_PREFERRED_ADDRESS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SEND_DISABLE_ACTIVE_MIGRATION_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_DEBUG_VISITOR_CONFIG_FIELD_NUMBER: _ClassVar[int]
    SAVE_CMSG_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REJECT_NEW_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    quic_protocol_options: _protocol_pb2.QuicProtocolOptions
    idle_timeout: _duration_pb2.Duration
    crypto_handshake_timeout: _duration_pb2.Duration
    enabled: _base_pb2.RuntimeFeatureFlag
    packets_to_read_to_connection_count_ratio: _wrappers_pb2.UInt32Value
    crypto_stream_config: _extension_pb2.TypedExtensionConfig
    proof_source_config: _extension_pb2.TypedExtensionConfig
    connection_id_generator_config: _extension_pb2.TypedExtensionConfig
    server_preferred_address_config: _extension_pb2.TypedExtensionConfig
    send_disable_active_migration: _wrappers_pb2.BoolValue
    connection_debug_visitor_config: _extension_pb2.TypedExtensionConfig
    save_cmsg_config: _containers.RepeatedCompositeFieldContainer[_socket_cmsg_headers_pb2.SocketCmsgHeaders]
    reject_new_connections: bool
    def __init__(self, quic_protocol_options: _Optional[_Union[_protocol_pb2.QuicProtocolOptions, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., crypto_handshake_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., enabled: _Optional[_Union[_base_pb2.RuntimeFeatureFlag, _Mapping]] = ..., packets_to_read_to_connection_count_ratio: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., crypto_stream_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., proof_source_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., connection_id_generator_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., server_preferred_address_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., send_disable_active_migration: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., connection_debug_visitor_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., save_cmsg_config: _Optional[_Iterable[_Union[_socket_cmsg_headers_pb2.SocketCmsgHeaders, _Mapping]]] = ..., reject_new_connections: bool = ...) -> None: ...
