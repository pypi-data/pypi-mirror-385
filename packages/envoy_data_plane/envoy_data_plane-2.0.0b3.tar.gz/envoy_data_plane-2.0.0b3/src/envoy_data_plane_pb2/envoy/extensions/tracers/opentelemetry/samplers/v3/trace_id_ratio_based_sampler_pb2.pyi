from envoy.type.v3 import percent_pb2 as _percent_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TraceIdRatioBasedSamplerConfig(_message.Message):
    __slots__ = ("sampling_percentage",)
    SAMPLING_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    sampling_percentage: _percent_pb2.FractionalPercent
    def __init__(self, sampling_percentage: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ...) -> None: ...
