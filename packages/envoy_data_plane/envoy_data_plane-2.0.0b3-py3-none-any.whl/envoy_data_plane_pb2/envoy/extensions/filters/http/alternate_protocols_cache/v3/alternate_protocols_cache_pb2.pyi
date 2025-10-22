from envoy.config.core.v3 import protocol_pb2 as _protocol_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("alternate_protocols_cache_options",)
    ALTERNATE_PROTOCOLS_CACHE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    alternate_protocols_cache_options: _protocol_pb2.AlternateProtocolsCacheOptions
    def __init__(self, alternate_protocols_cache_options: _Optional[_Union[_protocol_pb2.AlternateProtocolsCacheOptions, _Mapping]] = ...) -> None: ...
