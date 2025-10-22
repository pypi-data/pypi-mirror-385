from envoy.config.common.mutation_rules.v3 import mutation_rules_pb2 as _mutation_rules_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HeaderMutation(_message.Message):
    __slots__ = ("mutations",)
    MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    mutations: _containers.RepeatedCompositeFieldContainer[_mutation_rules_pb2.HeaderMutation]
    def __init__(self, mutations: _Optional[_Iterable[_Union[_mutation_rules_pb2.HeaderMutation, _Mapping]]] = ...) -> None: ...
