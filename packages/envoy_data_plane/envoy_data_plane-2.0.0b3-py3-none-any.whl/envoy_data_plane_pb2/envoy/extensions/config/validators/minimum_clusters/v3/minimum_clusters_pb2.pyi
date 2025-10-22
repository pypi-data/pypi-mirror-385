from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MinimumClustersValidator(_message.Message):
    __slots__ = ("min_clusters_num",)
    MIN_CLUSTERS_NUM_FIELD_NUMBER: _ClassVar[int]
    min_clusters_num: int
    def __init__(self, min_clusters_num: _Optional[int] = ...) -> None: ...
