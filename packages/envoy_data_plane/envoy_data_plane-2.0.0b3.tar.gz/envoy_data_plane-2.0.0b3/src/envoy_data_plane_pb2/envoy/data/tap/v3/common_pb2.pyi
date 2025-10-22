from envoy.config.core.v3 import address_pb2 as _address_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Body(_message.Message):
    __slots__ = ("as_bytes", "as_string", "truncated")
    AS_BYTES_FIELD_NUMBER: _ClassVar[int]
    AS_STRING_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    as_bytes: bytes
    as_string: str
    truncated: bool
    def __init__(self, as_bytes: _Optional[bytes] = ..., as_string: _Optional[str] = ..., truncated: bool = ...) -> None: ...

class Connection(_message.Message):
    __slots__ = ("local_address", "remote_address")
    LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    local_address: _address_pb2.Address
    remote_address: _address_pb2.Address
    def __init__(self, local_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., remote_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ...) -> None: ...
