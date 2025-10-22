from envoy.extensions.transport_sockets.tls.v3 import tls_pb2 as _tls_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuicDownstreamTransport(_message.Message):
    __slots__ = ("downstream_tls_context", "enable_early_data")
    DOWNSTREAM_TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_EARLY_DATA_FIELD_NUMBER: _ClassVar[int]
    downstream_tls_context: _tls_pb2.DownstreamTlsContext
    enable_early_data: _wrappers_pb2.BoolValue
    def __init__(self, downstream_tls_context: _Optional[_Union[_tls_pb2.DownstreamTlsContext, _Mapping]] = ..., enable_early_data: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class QuicUpstreamTransport(_message.Message):
    __slots__ = ("upstream_tls_context",)
    UPSTREAM_TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    upstream_tls_context: _tls_pb2.UpstreamTlsContext
    def __init__(self, upstream_tls_context: _Optional[_Union[_tls_pb2.UpstreamTlsContext, _Mapping]] = ...) -> None: ...
