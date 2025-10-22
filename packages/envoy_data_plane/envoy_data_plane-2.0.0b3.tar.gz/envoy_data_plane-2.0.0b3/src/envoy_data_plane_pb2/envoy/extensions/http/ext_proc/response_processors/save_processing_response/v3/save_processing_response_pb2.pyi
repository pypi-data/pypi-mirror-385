from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SaveProcessingResponse(_message.Message):
    __slots__ = ("filter_state_name_suffix", "save_request_headers", "save_response_headers", "save_request_trailers", "save_response_trailers", "save_immediate_response")
    class SaveOptions(_message.Message):
        __slots__ = ("save_response", "save_on_error")
        SAVE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
        SAVE_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
        save_response: bool
        save_on_error: bool
        def __init__(self, save_response: bool = ..., save_on_error: bool = ...) -> None: ...
    FILTER_STATE_NAME_SUFFIX_FIELD_NUMBER: _ClassVar[int]
    SAVE_REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    SAVE_RESPONSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    SAVE_REQUEST_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    SAVE_RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    SAVE_IMMEDIATE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    filter_state_name_suffix: str
    save_request_headers: SaveProcessingResponse.SaveOptions
    save_response_headers: SaveProcessingResponse.SaveOptions
    save_request_trailers: SaveProcessingResponse.SaveOptions
    save_response_trailers: SaveProcessingResponse.SaveOptions
    save_immediate_response: SaveProcessingResponse.SaveOptions
    def __init__(self, filter_state_name_suffix: _Optional[str] = ..., save_request_headers: _Optional[_Union[SaveProcessingResponse.SaveOptions, _Mapping]] = ..., save_response_headers: _Optional[_Union[SaveProcessingResponse.SaveOptions, _Mapping]] = ..., save_request_trailers: _Optional[_Union[SaveProcessingResponse.SaveOptions, _Mapping]] = ..., save_response_trailers: _Optional[_Union[SaveProcessingResponse.SaveOptions, _Mapping]] = ..., save_immediate_response: _Optional[_Union[SaveProcessingResponse.SaveOptions, _Mapping]] = ...) -> None: ...
