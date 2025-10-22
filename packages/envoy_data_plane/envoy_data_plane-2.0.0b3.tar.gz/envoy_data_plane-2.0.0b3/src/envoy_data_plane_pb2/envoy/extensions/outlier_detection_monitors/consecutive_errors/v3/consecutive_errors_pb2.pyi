from envoy.extensions.outlier_detection_monitors.common.v3 import error_types_pb2 as _error_types_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConsecutiveErrors(_message.Message):
    __slots__ = ("name", "threshold", "enforcing", "error_buckets")
    NAME_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    ENFORCING_FIELD_NUMBER: _ClassVar[int]
    ERROR_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    name: str
    threshold: _wrappers_pb2.UInt32Value
    enforcing: _wrappers_pb2.UInt32Value
    error_buckets: _error_types_pb2.ErrorBuckets
    def __init__(self, name: _Optional[str] = ..., threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforcing: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., error_buckets: _Optional[_Union[_error_types_pb2.ErrorBuckets, _Mapping]] = ...) -> None: ...
