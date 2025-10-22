from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.type.metadata.v3 import metadata_pb2 as _metadata_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InternalUpstreamTransport(_message.Message):
    __slots__ = ("passthrough_metadata", "transport_socket")
    class MetadataValueSource(_message.Message):
        __slots__ = ("kind", "name")
        KIND_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        kind: _metadata_pb2.MetadataKind
        name: str
        def __init__(self, kind: _Optional[_Union[_metadata_pb2.MetadataKind, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...
    PASSTHROUGH_METADATA_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
    passthrough_metadata: _containers.RepeatedCompositeFieldContainer[InternalUpstreamTransport.MetadataValueSource]
    transport_socket: _base_pb2.TransportSocket
    def __init__(self, passthrough_metadata: _Optional[_Iterable[_Union[InternalUpstreamTransport.MetadataValueSource, _Mapping]]] = ..., transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ...) -> None: ...
