from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParentBasedSamplerConfig(_message.Message):
    __slots__ = ("wrapped_sampler",)
    WRAPPED_SAMPLER_FIELD_NUMBER: _ClassVar[int]
    wrapped_sampler: _extension_pb2.TypedExtensionConfig
    def __init__(self, wrapped_sampler: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
