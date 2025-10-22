from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import any_pb2 as _any_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamEventsRequest(_message.Message):
    __slots__ = ("identifier", "events")
    class Identifier(_message.Message):
        __slots__ = ("node",)
        NODE_FIELD_NUMBER: _ClassVar[int]
        node: _base_pb2.Node
        def __init__(self, node: _Optional[_Union[_base_pb2.Node, _Mapping]] = ...) -> None: ...
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    identifier: StreamEventsRequest.Identifier
    events: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, identifier: _Optional[_Union[StreamEventsRequest.Identifier, _Mapping]] = ..., events: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...

class StreamEventsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
