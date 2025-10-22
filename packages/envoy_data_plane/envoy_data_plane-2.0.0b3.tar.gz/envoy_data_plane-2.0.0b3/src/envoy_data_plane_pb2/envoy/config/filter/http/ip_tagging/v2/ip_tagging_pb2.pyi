from envoy.api.v2.core import address_pb2 as _address_pb2
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

class IPTagging(_message.Message):
    __slots__ = ("request_type", "ip_tags")
    class RequestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BOTH: _ClassVar[IPTagging.RequestType]
        INTERNAL: _ClassVar[IPTagging.RequestType]
        EXTERNAL: _ClassVar[IPTagging.RequestType]
    BOTH: IPTagging.RequestType
    INTERNAL: IPTagging.RequestType
    EXTERNAL: IPTagging.RequestType
    class IPTag(_message.Message):
        __slots__ = ("ip_tag_name", "ip_list")
        IP_TAG_NAME_FIELD_NUMBER: _ClassVar[int]
        IP_LIST_FIELD_NUMBER: _ClassVar[int]
        ip_tag_name: str
        ip_list: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
        def __init__(self, ip_tag_name: _Optional[str] = ..., ip_list: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ...) -> None: ...
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    IP_TAGS_FIELD_NUMBER: _ClassVar[int]
    request_type: IPTagging.RequestType
    ip_tags: _containers.RepeatedCompositeFieldContainer[IPTagging.IPTag]
    def __init__(self, request_type: _Optional[_Union[IPTagging.RequestType, str]] = ..., ip_tags: _Optional[_Iterable[_Union[IPTagging.IPTag, _Mapping]]] = ...) -> None: ...
