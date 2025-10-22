from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAddrInfoDnsResolverConfig(_message.Message):
    __slots__ = ("num_retries", "num_resolver_threads")
    NUM_RETRIES_FIELD_NUMBER: _ClassVar[int]
    NUM_RESOLVER_THREADS_FIELD_NUMBER: _ClassVar[int]
    num_retries: _wrappers_pb2.UInt32Value
    num_resolver_threads: _wrappers_pb2.UInt32Value
    def __init__(self, num_retries: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., num_resolver_threads: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
