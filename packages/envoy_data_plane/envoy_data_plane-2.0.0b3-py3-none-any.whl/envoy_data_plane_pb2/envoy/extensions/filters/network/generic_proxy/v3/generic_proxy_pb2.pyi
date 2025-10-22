from envoy.config.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.extensions.filters.network.generic_proxy.v3 import route_pb2 as _route_pb2
from envoy.extensions.filters.network.http_connection_manager.v3 import http_connection_manager_pb2 as _http_connection_manager_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenericProxy(_message.Message):
    __slots__ = ("stat_prefix", "codec_config", "generic_rds", "route_config", "filters", "tracing", "access_log")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CODEC_CONFIG_FIELD_NUMBER: _ClassVar[int]
    GENERIC_RDS_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    TRACING_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    codec_config: _extension_pb2.TypedExtensionConfig
    generic_rds: GenericRds
    route_config: _route_pb2.RouteConfiguration
    filters: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    tracing: _http_connection_manager_pb2.HttpConnectionManager.Tracing
    access_log: _containers.RepeatedCompositeFieldContainer[_accesslog_pb2.AccessLog]
    def __init__(self, stat_prefix: _Optional[str] = ..., codec_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., generic_rds: _Optional[_Union[GenericRds, _Mapping]] = ..., route_config: _Optional[_Union[_route_pb2.RouteConfiguration, _Mapping]] = ..., filters: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., tracing: _Optional[_Union[_http_connection_manager_pb2.HttpConnectionManager.Tracing, _Mapping]] = ..., access_log: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLog, _Mapping]]] = ...) -> None: ...

class GenericRds(_message.Message):
    __slots__ = ("config_source", "route_config_name")
    CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_CONFIG_NAME_FIELD_NUMBER: _ClassVar[int]
    config_source: _config_source_pb2.ConfigSource
    route_config_name: str
    def __init__(self, config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., route_config_name: _Optional[str] = ...) -> None: ...
