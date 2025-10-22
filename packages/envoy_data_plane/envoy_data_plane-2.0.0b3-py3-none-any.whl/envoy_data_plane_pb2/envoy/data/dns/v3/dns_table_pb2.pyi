import datetime

from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DnsTable(_message.Message):
    __slots__ = ("external_retry_count", "virtual_domains", "known_suffixes")
    class AddressList(_message.Message):
        __slots__ = ("address",)
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        address: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, address: _Optional[_Iterable[str]] = ...) -> None: ...
    class DnsServiceProtocol(_message.Message):
        __slots__ = ("number", "name")
        NUMBER_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        number: int
        name: str
        def __init__(self, number: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...
    class DnsServiceTarget(_message.Message):
        __slots__ = ("host_name", "cluster_name", "priority", "weight", "port")
        HOST_NAME_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
        PRIORITY_FIELD_NUMBER: _ClassVar[int]
        WEIGHT_FIELD_NUMBER: _ClassVar[int]
        PORT_FIELD_NUMBER: _ClassVar[int]
        host_name: str
        cluster_name: str
        priority: int
        weight: int
        port: int
        def __init__(self, host_name: _Optional[str] = ..., cluster_name: _Optional[str] = ..., priority: _Optional[int] = ..., weight: _Optional[int] = ..., port: _Optional[int] = ...) -> None: ...
    class DnsService(_message.Message):
        __slots__ = ("service_name", "protocol", "ttl", "targets")
        SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        PROTOCOL_FIELD_NUMBER: _ClassVar[int]
        TTL_FIELD_NUMBER: _ClassVar[int]
        TARGETS_FIELD_NUMBER: _ClassVar[int]
        service_name: str
        protocol: DnsTable.DnsServiceProtocol
        ttl: _duration_pb2.Duration
        targets: _containers.RepeatedCompositeFieldContainer[DnsTable.DnsServiceTarget]
        def __init__(self, service_name: _Optional[str] = ..., protocol: _Optional[_Union[DnsTable.DnsServiceProtocol, _Mapping]] = ..., ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., targets: _Optional[_Iterable[_Union[DnsTable.DnsServiceTarget, _Mapping]]] = ...) -> None: ...
    class DnsServiceList(_message.Message):
        __slots__ = ("services",)
        SERVICES_FIELD_NUMBER: _ClassVar[int]
        services: _containers.RepeatedCompositeFieldContainer[DnsTable.DnsService]
        def __init__(self, services: _Optional[_Iterable[_Union[DnsTable.DnsService, _Mapping]]] = ...) -> None: ...
    class DnsEndpoint(_message.Message):
        __slots__ = ("address_list", "cluster_name", "service_list")
        ADDRESS_LIST_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
        SERVICE_LIST_FIELD_NUMBER: _ClassVar[int]
        address_list: DnsTable.AddressList
        cluster_name: str
        service_list: DnsTable.DnsServiceList
        def __init__(self, address_list: _Optional[_Union[DnsTable.AddressList, _Mapping]] = ..., cluster_name: _Optional[str] = ..., service_list: _Optional[_Union[DnsTable.DnsServiceList, _Mapping]] = ...) -> None: ...
    class DnsVirtualDomain(_message.Message):
        __slots__ = ("name", "endpoint", "answer_ttl")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ENDPOINT_FIELD_NUMBER: _ClassVar[int]
        ANSWER_TTL_FIELD_NUMBER: _ClassVar[int]
        name: str
        endpoint: DnsTable.DnsEndpoint
        answer_ttl: _duration_pb2.Duration
        def __init__(self, name: _Optional[str] = ..., endpoint: _Optional[_Union[DnsTable.DnsEndpoint, _Mapping]] = ..., answer_ttl: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    EXTERNAL_RETRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_DOMAINS_FIELD_NUMBER: _ClassVar[int]
    KNOWN_SUFFIXES_FIELD_NUMBER: _ClassVar[int]
    external_retry_count: int
    virtual_domains: _containers.RepeatedCompositeFieldContainer[DnsTable.DnsVirtualDomain]
    known_suffixes: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    def __init__(self, external_retry_count: _Optional[int] = ..., virtual_domains: _Optional[_Iterable[_Union[DnsTable.DnsVirtualDomain, _Mapping]]] = ..., known_suffixes: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ...) -> None: ...
