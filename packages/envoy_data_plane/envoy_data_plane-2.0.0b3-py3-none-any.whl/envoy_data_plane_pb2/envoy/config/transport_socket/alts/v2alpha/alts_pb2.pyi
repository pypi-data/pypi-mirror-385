from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Alts(_message.Message):
    __slots__ = ("handshaker_service", "peer_service_accounts")
    HANDSHAKER_SERVICE_FIELD_NUMBER: _ClassVar[int]
    PEER_SERVICE_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    handshaker_service: str
    peer_service_accounts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, handshaker_service: _Optional[str] = ..., peer_service_accounts: _Optional[_Iterable[str]] = ...) -> None: ...
