from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.extensions.filters.network.thrift_proxy.v3 import route_pb2 as _route_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
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

class Trds(_message.Message):
    __slots__ = ("config_source", "route_config_name")
    CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_NAME_FIELD_NUMBER: _ClassVar[int]
    config_source: _config_source_pb2.ConfigSource
    route_config_name: str
    def __init__(self, config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., route_config_name: _Optional[str] = ...) -> None: ...

class ThriftProxy(_message.Message):
    __slots__ = ("transport", "protocol", "stat_prefix", "route_config", "trds", "thrift_filters", "payload_passthrough", "max_requests_per_connection", "access_log", "header_keys_preserve_case")
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TRDS_FIELD_NUMBER: _ClassVar[int]
    THRIFT_FILTERS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_PASSTHROUGH_FIELD_NUMBER: _ClassVar[int]
    MAX_REQUESTS_PER_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    HEADER_KEYS_PRESERVE_CASE_FIELD_NUMBER: _ClassVar[int]
    transport: TransportType
    protocol: ProtocolType
    stat_prefix: str
    route_config: _route_pb2.RouteConfiguration
    trds: Trds
    thrift_filters: _containers.RepeatedCompositeFieldContainer[ThriftFilter]
    payload_passthrough: bool
    max_requests_per_connection: _wrappers_pb2.UInt32Value
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    header_keys_preserve_case: bool
    def __init__(self, transport: _Optional[_Union[TransportType, str]] = ..., protocol: _Optional[_Union[ProtocolType, str]] = ..., stat_prefix: _Optional[str] = ..., route_config: _Optional[_Union[_route_pb2.RouteConfiguration, _Mapping]] = ..., trds: _Optional[_Union[Trds, _Mapping]] = ..., thrift_filters: _Optional[_Iterable[_Union[ThriftFilter, _Mapping]]] = ..., payload_passthrough: bool = ..., max_requests_per_connection: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ..., header_keys_preserve_case: bool = ...) -> None: ...

class ThriftFilter(_message.Message):
    __slots__ = ("name", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ThriftProtocolOptions(_message.Message):
    __slots__ = ("transport", "protocol")
    TRANSPORT_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    transport: TransportType
    protocol: ProtocolType
    def __init__(self, transport: _Optional[_Union[TransportType, str]] = ..., protocol: _Optional[_Union[ProtocolType, str]] = ...) -> None: ...
