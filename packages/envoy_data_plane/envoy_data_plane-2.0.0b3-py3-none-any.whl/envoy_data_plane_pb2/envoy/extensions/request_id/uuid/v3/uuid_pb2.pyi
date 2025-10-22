from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UuidRequestIdConfig(_message.Message):
    __slots__ = ("pack_trace_reason", "use_request_id_for_trace_sampling")
    PACK_TRACE_REASON_FIELD_NUMBER: _ClassVar[int]
    USE_REQUEST_ID_FOR_TRACE_SAMPLING_FIELD_NUMBER: _ClassVar[int]
    pack_trace_reason: _wrappers_pb2.BoolValue
    use_request_id_for_trace_sampling: _wrappers_pb2.BoolValue
    def __init__(self, pack_trace_reason: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., use_request_id_for_trace_sampling: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...
