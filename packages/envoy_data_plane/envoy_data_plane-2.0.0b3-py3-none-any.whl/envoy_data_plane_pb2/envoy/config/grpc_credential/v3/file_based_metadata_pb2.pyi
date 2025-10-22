from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileBasedMetadataConfig(_message.Message):
    __slots__ = ("secret_data", "header_key", "header_prefix")
    SECRET_DATA_FIELD_NUMBER: _ClassVar[int]
    HEADER_KEY_FIELD_NUMBER: _ClassVar[int]
    HEADER_PREFIX_FIELD_NUMBER: _ClassVar[int]
    secret_data: _base_pb2.DataSource
    header_key: str
    header_prefix: str
    def __init__(self, secret_data: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., header_key: _Optional[str] = ..., header_prefix: _Optional[str] = ...) -> None: ...
