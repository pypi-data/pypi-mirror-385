from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HashPolicy(_message.Message):
    __slots__ = ("source_ip",)
    class SourceIp(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    SOURCE_IP_FIELD_NUMBER: _ClassVar[int]
    source_ip: HashPolicy.SourceIp
    def __init__(self, source_ip: _Optional[_Union[HashPolicy.SourceIp, _Mapping]] = ...) -> None: ...
