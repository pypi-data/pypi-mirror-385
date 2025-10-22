from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PathTransformation(_message.Message):
    __slots__ = ("operations",)
    class Operation(_message.Message):
        __slots__ = ("normalize_path_rfc_3986", "merge_slashes")
        class NormalizePathRFC3986(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class MergeSlashes(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        NORMALIZE_PATH_RFC_3986_FIELD_NUMBER: _ClassVar[int]
        MERGE_SLASHES_FIELD_NUMBER: _ClassVar[int]
        normalize_path_rfc_3986: PathTransformation.Operation.NormalizePathRFC3986
        merge_slashes: PathTransformation.Operation.MergeSlashes
        def __init__(self, normalize_path_rfc_3986: _Optional[_Union[PathTransformation.Operation.NormalizePathRFC3986, _Mapping]] = ..., merge_slashes: _Optional[_Union[PathTransformation.Operation.MergeSlashes, _Mapping]] = ...) -> None: ...
    OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    operations: _containers.RepeatedCompositeFieldContainer[PathTransformation.Operation]
    def __init__(self, operations: _Optional[_Iterable[_Union[PathTransformation.Operation, _Mapping]]] = ...) -> None: ...
