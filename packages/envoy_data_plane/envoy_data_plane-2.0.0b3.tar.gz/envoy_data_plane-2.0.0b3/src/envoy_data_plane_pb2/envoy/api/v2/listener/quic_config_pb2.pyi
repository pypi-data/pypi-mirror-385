import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuicProtocolOptions(_message.Message):
    __slots__ = ("max_concurrent_streams", "idle_timeout", "crypto_handshake_timeout")
    MAX_CONCURRENT_STREAMS_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    CRYPTO_HANDSHAKE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    max_concurrent_streams: _wrappers_pb2.UInt32Value
    idle_timeout: _duration_pb2.Duration
    crypto_handshake_timeout: _duration_pb2.Duration
    def __init__(self, max_concurrent_streams: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., crypto_handshake_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
