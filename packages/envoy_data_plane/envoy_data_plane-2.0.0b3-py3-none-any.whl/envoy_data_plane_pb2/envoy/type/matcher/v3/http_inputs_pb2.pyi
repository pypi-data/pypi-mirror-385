from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HttpRequestHeaderMatchInput(_message.Message):
    __slots__ = ("header_name",)
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    header_name: str
    def __init__(self, header_name: _Optional[str] = ...) -> None: ...

class HttpRequestTrailerMatchInput(_message.Message):
    __slots__ = ("header_name",)
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    header_name: str
    def __init__(self, header_name: _Optional[str] = ...) -> None: ...

class HttpResponseHeaderMatchInput(_message.Message):
    __slots__ = ("header_name",)
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    header_name: str
    def __init__(self, header_name: _Optional[str] = ...) -> None: ...

class HttpResponseTrailerMatchInput(_message.Message):
    __slots__ = ("header_name",)
    HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
    header_name: str
    def __init__(self, header_name: _Optional[str] = ...) -> None: ...

class HttpRequestQueryParamMatchInput(_message.Message):
    __slots__ = ("query_param",)
    QUERY_PARAM_FIELD_NUMBER: _ClassVar[int]
    query_param: str
    def __init__(self, query_param: _Optional[str] = ...) -> None: ...
