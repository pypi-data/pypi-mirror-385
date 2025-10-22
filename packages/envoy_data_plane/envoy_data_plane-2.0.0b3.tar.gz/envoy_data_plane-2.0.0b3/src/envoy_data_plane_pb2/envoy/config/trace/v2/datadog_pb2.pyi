from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DatadogConfig(_message.Message):
    __slots__ = ("collector_cluster", "service_name")
    COLLECTOR_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    collector_cluster: str
    service_name: str
    def __init__(self, collector_cluster: _Optional[str] = ..., service_name: _Optional[str] = ...) -> None: ...
