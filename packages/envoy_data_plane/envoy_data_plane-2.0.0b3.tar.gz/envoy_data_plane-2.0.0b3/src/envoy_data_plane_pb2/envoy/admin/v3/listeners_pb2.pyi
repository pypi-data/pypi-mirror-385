from envoy.config.core.v3 import address_pb2 as _address_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Listeners(_message.Message):
    __slots__ = ("listener_statuses",)
    LISTENER_STATUSES_FIELD_NUMBER: _ClassVar[int]
    listener_statuses: _containers.RepeatedCompositeFieldContainer[ListenerStatus]
    def __init__(self, listener_statuses: _Optional[_Iterable[_Union[ListenerStatus, _Mapping]]] = ...) -> None: ...

class ListenerStatus(_message.Message):
    __slots__ = ("name", "local_address", "additional_local_addresses")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_LOCAL_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    name: str
    local_address: _address_pb2.Address
    additional_local_addresses: _containers.RepeatedCompositeFieldContainer[_address_pb2.Address]
    def __init__(self, name: _Optional[str] = ..., local_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., additional_local_addresses: _Optional[_Iterable[_Union[_address_pb2.Address, _Mapping]]] = ...) -> None: ...
