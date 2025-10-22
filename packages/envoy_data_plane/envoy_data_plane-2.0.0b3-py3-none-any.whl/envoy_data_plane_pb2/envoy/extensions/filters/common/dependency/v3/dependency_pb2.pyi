from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Dependency(_message.Message):
    __slots__ = ("type", "name")
    class DependencyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HEADER: _ClassVar[Dependency.DependencyType]
        FILTER_STATE_KEY: _ClassVar[Dependency.DependencyType]
        DYNAMIC_METADATA: _ClassVar[Dependency.DependencyType]
    HEADER: Dependency.DependencyType
    FILTER_STATE_KEY: Dependency.DependencyType
    DYNAMIC_METADATA: Dependency.DependencyType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    type: Dependency.DependencyType
    name: str
    def __init__(self, type: _Optional[_Union[Dependency.DependencyType, str]] = ..., name: _Optional[str] = ...) -> None: ...

class FilterDependencies(_message.Message):
    __slots__ = ("decode_required", "decode_provided", "encode_required", "encode_provided")
    DECODE_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DECODE_PROVIDED_FIELD_NUMBER: _ClassVar[int]
    ENCODE_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    ENCODE_PROVIDED_FIELD_NUMBER: _ClassVar[int]
    decode_required: _containers.RepeatedCompositeFieldContainer[Dependency]
    decode_provided: _containers.RepeatedCompositeFieldContainer[Dependency]
    encode_required: _containers.RepeatedCompositeFieldContainer[Dependency]
    encode_provided: _containers.RepeatedCompositeFieldContainer[Dependency]
    def __init__(self, decode_required: _Optional[_Iterable[_Union[Dependency, _Mapping]]] = ..., decode_provided: _Optional[_Iterable[_Union[Dependency, _Mapping]]] = ..., encode_required: _Optional[_Iterable[_Union[Dependency, _Mapping]]] = ..., encode_provided: _Optional[_Iterable[_Union[Dependency, _Mapping]]] = ...) -> None: ...

class MatchingRequirements(_message.Message):
    __slots__ = ("data_input_allow_list",)
    class DataInputAllowList(_message.Message):
        __slots__ = ("type_url",)
        TYPE_URL_FIELD_NUMBER: _ClassVar[int]
        type_url: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, type_url: _Optional[_Iterable[str]] = ...) -> None: ...
    DATA_INPUT_ALLOW_LIST_FIELD_NUMBER: _ClassVar[int]
    data_input_allow_list: MatchingRequirements.DataInputAllowList
    def __init__(self, data_input_allow_list: _Optional[_Union[MatchingRequirements.DataInputAllowList, _Mapping]] = ...) -> None: ...
