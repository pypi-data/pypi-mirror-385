from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DestinationIPInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DestinationPortInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SourceIPInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SourcePortInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DirectSourceIPInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SourceTypeInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ServerNameInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TransportProtocolInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ApplicationProtocolInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FilterStateInput(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class DynamicMetadataInput(_message.Message):
    __slots__ = ("filter", "path")
    class PathSegment(_message.Message):
        __slots__ = ("key",)
        KEY_FIELD_NUMBER: _ClassVar[int]
        key: str
        def __init__(self, key: _Optional[str] = ...) -> None: ...
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    filter: str
    path: _containers.RepeatedCompositeFieldContainer[DynamicMetadataInput.PathSegment]
    def __init__(self, filter: _Optional[str] = ..., path: _Optional[_Iterable[_Union[DynamicMetadataInput.PathSegment, _Mapping]]] = ...) -> None: ...

class NetworkNamespaceInput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
