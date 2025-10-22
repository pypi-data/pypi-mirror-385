from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Pipe(_message.Message):
    __slots__ = ("path", "mode")
    PATH_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    path: str
    mode: int
    def __init__(self, path: _Optional[str] = ..., mode: _Optional[int] = ...) -> None: ...

class SocketAddress(_message.Message):
    __slots__ = ("protocol", "address", "port_value", "named_port", "resolver_name", "ipv4_compat")
    class Protocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TCP: _ClassVar[SocketAddress.Protocol]
        UDP: _ClassVar[SocketAddress.Protocol]
    TCP: SocketAddress.Protocol
    UDP: SocketAddress.Protocol
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PORT_VALUE_FIELD_NUMBER: _ClassVar[int]
    NAMED_PORT_FIELD_NUMBER: _ClassVar[int]
    RESOLVER_NAME_FIELD_NUMBER: _ClassVar[int]
    IPV4_COMPAT_FIELD_NUMBER: _ClassVar[int]
    protocol: SocketAddress.Protocol
    address: str
    port_value: int
    named_port: str
    resolver_name: str
    ipv4_compat: bool
    def __init__(self, protocol: _Optional[_Union[SocketAddress.Protocol, str]] = ..., address: _Optional[str] = ..., port_value: _Optional[int] = ..., named_port: _Optional[str] = ..., resolver_name: _Optional[str] = ..., ipv4_compat: bool = ...) -> None: ...

class TcpKeepalive(_message.Message):
    __slots__ = ("keepalive_probes", "keepalive_time", "keepalive_interval")
    KEEPALIVE_PROBES_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVE_TIME_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    keepalive_probes: _wrappers_pb2.UInt32Value
    keepalive_time: _wrappers_pb2.UInt32Value
    keepalive_interval: _wrappers_pb2.UInt32Value
    def __init__(self, keepalive_probes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., keepalive_time: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., keepalive_interval: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class BindConfig(_message.Message):
    __slots__ = ("source_address", "freebind", "socket_options")
    SOURCE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    FREEBIND_FIELD_NUMBER: _ClassVar[int]
    SOCKET_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    source_address: SocketAddress
    freebind: _wrappers_pb2.BoolValue
    socket_options: _containers.RepeatedCompositeFieldContainer[_socket_option_pb2.SocketOption]
    def __init__(self, source_address: _Optional[_Union[SocketAddress, _Mapping]] = ..., freebind: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., socket_options: _Optional[_Iterable[_Union[_socket_option_pb2.SocketOption, _Mapping]]] = ...) -> None: ...

class Address(_message.Message):
    __slots__ = ("socket_address", "pipe")
    SOCKET_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PIPE_FIELD_NUMBER: _ClassVar[int]
    socket_address: SocketAddress
    pipe: Pipe
    def __init__(self, socket_address: _Optional[_Union[SocketAddress, _Mapping]] = ..., pipe: _Optional[_Union[Pipe, _Mapping]] = ...) -> None: ...

class CidrRange(_message.Message):
    __slots__ = ("address_prefix", "prefix_len")
    ADDRESS_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PREFIX_LEN_FIELD_NUMBER: _ClassVar[int]
    address_prefix: str
    prefix_len: _wrappers_pb2.UInt32Value
    def __init__(self, address_prefix: _Optional[str] = ..., prefix_len: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
