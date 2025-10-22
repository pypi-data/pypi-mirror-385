from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("upgrade_protobuf_to_grpc", "ignore_query_parameters")
    UPGRADE_PROTOBUF_TO_GRPC_FIELD_NUMBER: _ClassVar[int]
    IGNORE_QUERY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    upgrade_protobuf_to_grpc: bool
    ignore_query_parameters: bool
    def __init__(self, upgrade_protobuf_to_grpc: bool = ..., ignore_query_parameters: bool = ...) -> None: ...
