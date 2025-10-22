from envoy.config.filter.network.thrift_proxy.v2alpha1 import route_pb2 as _route_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
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

class TransportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTO_TRANSPORT: _ClassVar[TransportType]
    FRAMED: _ClassVar[TransportType]
    UNFRAMED: _ClassVar[TransportType]
    HEADER: _ClassVar[TransportType]

class ProtocolType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTO_PROTOCOL: _ClassVar[ProtocolType]
    BINARY: _ClassVar[ProtocolType]
    LAX_BINARY: _ClassVar[ProtocolType]
    COMPACT: _ClassVar[ProtocolType]
    TWITTER: _ClassVar[ProtocolType]
AUTO_TRANSPORT: TransportType
FRAMED: TransportType
UNFRAMED: TransportType
HEADER: TransportType
AUTO_PROTOCOL: ProtocolType
BINARY: ProtocolType
LAX_BINARY: ProtocolType
COMPACT: ProtocolType
TWITTER: ProtocolType

class ThriftProxy(_message.Message):
    __slots__ = ("transport", "protocol", "stat_prefix", "route_config", "thrift_filters")
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    THRIFT_FILTERS_FIELD_NUMBER: _ClassVar[int]
    transport: TransportType
    protocol: ProtocolType
    stat_prefix: str
    route_config: _route_pb2.RouteConfiguration
    thrift_filters: _containers.RepeatedCompositeFieldContainer[ThriftFilter]
    def __init__(self, transport: _Optional[_Union[TransportType, str]] = ..., protocol: _Optional[_Union[ProtocolType, str]] = ..., stat_prefix: _Optional[str] = ..., route_config: _Optional[_Union[_route_pb2.RouteConfiguration, _Mapping]] = ..., thrift_filters: _Optional[_Iterable[_Union[ThriftFilter, _Mapping]]] = ...) -> None: ...

class ThriftFilter(_message.Message):
    __slots__ = ("name", "config", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _struct_pb2.Struct
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ThriftProtocolOptions(_message.Message):
    __slots__ = ("transport", "protocol")
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    transport: TransportType
    protocol: ProtocolType
    def __init__(self, transport: _Optional[_Union[TransportType, str]] = ..., protocol: _Optional[_Union[ProtocolType, str]] = ...) -> None: ...
