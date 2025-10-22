from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OmitHostMetadataConfig(_message.Message):
    __slots__ = ("metadata_match",)
    METADATA_MATCH_FIELD_NUMBER: _ClassVar[int]
    metadata_match: _base_pb2.Metadata
    def __init__(self, metadata_match: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ...) -> None: ...
