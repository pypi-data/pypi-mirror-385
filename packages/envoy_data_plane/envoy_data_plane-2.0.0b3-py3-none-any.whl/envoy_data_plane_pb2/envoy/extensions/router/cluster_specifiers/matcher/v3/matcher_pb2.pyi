from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClusterAction(_message.Message):
    __slots__ = ("cluster",)
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    cluster: str
    def __init__(self, cluster: _Optional[str] = ...) -> None: ...

class MatcherClusterSpecifier(_message.Message):
    __slots__ = ("cluster_matcher",)
    CLUSTER_MATCHER_FIELD_NUMBER: _ClassVar[int]
    cluster_matcher: _matcher_pb2.Matcher
    def __init__(self, cluster_matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ...) -> None: ...
