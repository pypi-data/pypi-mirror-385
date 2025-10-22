from envoy.config.core.v3 import grpc_method_list_pb2 as _grpc_method_list_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterConfig(_message.Message):
    __slots__ = ("emit_filter_state", "individual_method_stats_allowlist", "stats_for_all_methods", "enable_upstream_stats", "replace_dots_in_grpc_service_name")
    EMIT_FILTER_STATE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_METHOD_STATS_ALLOWLIST_FIELD_NUMBER: _ClassVar[int]
    STATS_FOR_ALL_METHODS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_UPSTREAM_STATS_FIELD_NUMBER: _ClassVar[int]
    REPLACE_DOTS_IN_GRPC_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    emit_filter_state: bool
    individual_method_stats_allowlist: _grpc_method_list_pb2.GrpcMethodList
    stats_for_all_methods: _wrappers_pb2.BoolValue
    enable_upstream_stats: bool
    replace_dots_in_grpc_service_name: bool
    def __init__(self, emit_filter_state: bool = ..., individual_method_stats_allowlist: _Optional[_Union[_grpc_method_list_pb2.GrpcMethodList, _Mapping]] = ..., stats_for_all_methods: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., enable_upstream_stats: bool = ..., replace_dots_in_grpc_service_name: bool = ...) -> None: ...

class FilterObject(_message.Message):
    __slots__ = ("request_message_count", "response_message_count")
    REQUEST_MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    request_message_count: int
    response_message_count: int
    def __init__(self, request_message_count: _Optional[int] = ..., response_message_count: _Optional[int] = ...) -> None: ...
