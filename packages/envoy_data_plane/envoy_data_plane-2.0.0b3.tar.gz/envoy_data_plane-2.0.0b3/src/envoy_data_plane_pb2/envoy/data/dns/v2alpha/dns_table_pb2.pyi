import datetime

from envoy.type.matcher import string_pb2 as _string_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
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
    class DnsEndpoint(_message.Message):
        __slots__ = ("address_list",)
        ADDRESS_LIST_FIELD_NUMBER: _ClassVar[int]
        address_list: DnsTable.AddressList
        def __init__(self, address_list: _Optional[_Union[DnsTable.AddressList, _Mapping]] = ...) -> None: ...
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
