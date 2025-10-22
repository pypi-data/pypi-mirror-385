from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.extensions.filters.network.dubbo_proxy.v3 import route_pb2 as _route_pb2
from google.protobuf import any_pb2 as _any_pb2
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

class ProtocolType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Dubbo: _ClassVar[ProtocolType]

class SerializationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Hessian2: _ClassVar[SerializationType]
Dubbo: ProtocolType
Hessian2: SerializationType

class Drds(_message.Message):
    __slots__ = ("config_source", "route_config_name")
    CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_NAME_FIELD_NUMBER: _ClassVar[int]
    config_source: _config_source_pb2.ConfigSource
    route_config_name: str
    def __init__(self, config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., route_config_name: _Optional[str] = ...) -> None: ...

class DubboProxy(_message.Message):
    __slots__ = ("stat_prefix", "protocol_type", "serialization_type", "route_config", "drds", "multiple_route_config", "dubbo_filters")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_TYPE_FIELD_NUMBER: _ClassVar[int]
    SERIALIZATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DRDS_FIELD_NUMBER: _ClassVar[int]
    MULTIPLE_ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DUBBO_FILTERS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    protocol_type: ProtocolType
    serialization_type: SerializationType
    route_config: _containers.RepeatedCompositeFieldContainer[_route_pb2.RouteConfiguration]
    drds: Drds
    multiple_route_config: _route_pb2.MultipleRouteConfiguration
    dubbo_filters: _containers.RepeatedCompositeFieldContainer[DubboFilter]
    def __init__(self, stat_prefix: _Optional[str] = ..., protocol_type: _Optional[_Union[ProtocolType, str]] = ..., serialization_type: _Optional[_Union[SerializationType, str]] = ..., route_config: _Optional[_Iterable[_Union[_route_pb2.RouteConfiguration, _Mapping]]] = ..., drds: _Optional[_Union[Drds, _Mapping]] = ..., multiple_route_config: _Optional[_Union[_route_pb2.MultipleRouteConfiguration, _Mapping]] = ..., dubbo_filters: _Optional[_Iterable[_Union[DubboFilter, _Mapping]]] = ...) -> None: ...

class DubboFilter(_message.Message):
    __slots__ = ("name", "config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
