from envoy.config.filter.network.dubbo_proxy.v2alpha1 import route_pb2 as _route_pb2
from google.protobuf import any_pb2 as _any_pb2
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

class ProtocolType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Dubbo: _ClassVar[ProtocolType]

class SerializationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Hessian2: _ClassVar[SerializationType]
Dubbo: ProtocolType
Hessian2: SerializationType

class DubboProxy(_message.Message):
    __slots__ = ("stat_prefix", "protocol_type", "serialization_type", "route_config", "dubbo_filters")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_TYPE_FIELD_NUMBER: _ClassVar[int]
    SERIALIZATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DUBBO_FILTERS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    protocol_type: ProtocolType
    serialization_type: SerializationType
    route_config: _containers.RepeatedCompositeFieldContainer[_route_pb2.RouteConfiguration]
    dubbo_filters: _containers.RepeatedCompositeFieldContainer[DubboFilter]
    def __init__(self, stat_prefix: _Optional[str] = ..., protocol_type: _Optional[_Union[ProtocolType, str]] = ..., serialization_type: _Optional[_Union[SerializationType, str]] = ..., route_config: _Optional[_Iterable[_Union[_route_pb2.RouteConfiguration, _Mapping]]] = ..., dubbo_filters: _Optional[_Iterable[_Union[DubboFilter, _Mapping]]] = ...) -> None: ...

class DubboFilter(_message.Message):
    __slots__ = ("name", "config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
