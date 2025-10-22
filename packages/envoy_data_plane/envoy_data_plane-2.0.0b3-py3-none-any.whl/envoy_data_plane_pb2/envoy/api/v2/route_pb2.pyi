from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import config_source_pb2 as _config_source_pb2
from envoy.api.v2.route import route_components_pb2 as _route_components_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RouteConfiguration(_message.Message):
    __slots__ = ("name", "virtual_hosts", "vhds", "internal_only_headers", "response_headers_to_add", "response_headers_to_remove", "request_headers_to_add", "request_headers_to_remove", "most_specific_header_mutations_wins", "validate_clusters")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_HOSTS_FIELD_NUMBER: _ClassVar[int]
    VHDS_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ONLY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_TO_REMOVE_FIELD_NUMBER: _ClassVar[int]
    MOST_SPECIFIC_HEADER_MUTATIONS_WINS_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    virtual_hosts: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.VirtualHost]
    vhds: Vhds
    internal_only_headers: _containers.RepeatedScalarFieldContainer[str]
    response_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    response_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    request_headers_to_add: _containers.RepeatedCompositeFieldContainer[_base_pb2.HeaderValueOption]
    request_headers_to_remove: _containers.RepeatedScalarFieldContainer[str]
    most_specific_header_mutations_wins: bool
    validate_clusters: _wrappers_pb2.BoolValue
    def __init__(self, name: _Optional[str] = ..., virtual_hosts: _Optional[_Iterable[_Union[_route_components_pb2.VirtualHost, _Mapping]]] = ..., vhds: _Optional[_Union[Vhds, _Mapping]] = ..., internal_only_headers: _Optional[_Iterable[str]] = ..., response_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., response_headers_to_remove: _Optional[_Iterable[str]] = ..., request_headers_to_add: _Optional[_Iterable[_Union[_base_pb2.HeaderValueOption, _Mapping]]] = ..., request_headers_to_remove: _Optional[_Iterable[str]] = ..., most_specific_header_mutations_wins: bool = ..., validate_clusters: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class Vhds(_message.Message):
    __slots__ = ("config_source",)
    CONFIG_SOURCE_FIELD_NUMBER: _ClassVar[int]
    config_source: _config_source_pb2.ConfigSource
    def __init__(self, config_source: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ...) -> None: ...
