import datetime

from envoy.api.v2.core import address_pb2 as _address_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientSSLAuth(_message.Message):
    __slots__ = ("auth_api_cluster", "stat_prefix", "refresh_delay", "ip_white_list")
    AUTH_API_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    REFRESH_DELAY_FIELD_NUMBER: _ClassVar[int]
    IP_WHITE_LIST_FIELD_NUMBER: _ClassVar[int]
    auth_api_cluster: str
    stat_prefix: str
    refresh_delay: _duration_pb2.Duration
    ip_white_list: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    def __init__(self, auth_api_cluster: _Optional[str] = ..., stat_prefix: _Optional[str] = ..., refresh_delay: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., ip_white_list: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ...) -> None: ...
