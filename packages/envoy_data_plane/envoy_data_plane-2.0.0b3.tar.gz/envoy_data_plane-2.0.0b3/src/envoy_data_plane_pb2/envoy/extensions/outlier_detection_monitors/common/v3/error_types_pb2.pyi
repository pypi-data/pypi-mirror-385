from envoy.type.v3 import range_pb2 as _range_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpErrors(_message.Message):
    __slots__ = ("range",)
    RANGE_FIELD_NUMBER: _ClassVar[int]
    range: _range_pb2.Int32Range
    def __init__(self, range: _Optional[_Union[_range_pb2.Int32Range, _Mapping]] = ...) -> None: ...

class LocalOriginErrors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DatabaseErrors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ErrorBuckets(_message.Message):
    __slots__ = ("http_errors", "local_origin_errors", "database_errors")
    HTTP_ERRORS_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ORIGIN_ERRORS_FIELD_NUMBER: _ClassVar[int]
    DATABASE_ERRORS_FIELD_NUMBER: _ClassVar[int]
    http_errors: _containers.RepeatedCompositeFieldContainer[HttpErrors]
    local_origin_errors: _containers.RepeatedCompositeFieldContainer[LocalOriginErrors]
    database_errors: _containers.RepeatedCompositeFieldContainer[DatabaseErrors]
    def __init__(self, http_errors: _Optional[_Iterable[_Union[HttpErrors, _Mapping]]] = ..., local_origin_errors: _Optional[_Iterable[_Union[LocalOriginErrors, _Mapping]]] = ..., database_errors: _Optional[_Iterable[_Union[DatabaseErrors, _Mapping]]] = ...) -> None: ...
