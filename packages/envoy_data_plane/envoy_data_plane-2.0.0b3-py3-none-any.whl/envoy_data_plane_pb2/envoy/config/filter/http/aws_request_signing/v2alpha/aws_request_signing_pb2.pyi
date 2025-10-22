from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AwsRequestSigning(_message.Message):
    __slots__ = ("service_name", "region", "host_rewrite")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    region: str
    host_rewrite: str
    def __init__(self, service_name: _Optional[str] = ..., region: _Optional[str] = ..., host_rewrite: _Optional[str] = ...) -> None: ...
