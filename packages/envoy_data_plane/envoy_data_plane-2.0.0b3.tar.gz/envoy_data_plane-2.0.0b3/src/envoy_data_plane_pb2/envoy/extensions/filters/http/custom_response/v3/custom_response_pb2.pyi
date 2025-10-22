from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CustomResponse(_message.Message):
    __slots__ = ("custom_response_matcher",)
    CUSTOM_RESPONSE_MATCHER_FIELD_NUMBER: _ClassVar[int]
    custom_response_matcher: _matcher_pb2.Matcher
    def __init__(self, custom_response_matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ...) -> None: ...
