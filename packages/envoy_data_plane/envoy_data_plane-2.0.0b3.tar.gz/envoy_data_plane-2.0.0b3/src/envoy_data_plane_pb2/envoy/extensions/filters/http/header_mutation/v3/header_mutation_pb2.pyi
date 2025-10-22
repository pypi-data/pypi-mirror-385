from envoy.config.common.mutation_rules.v3 import mutation_rules_pb2 as _mutation_rules_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Mutations(_message.Message):
    __slots__ = ("request_mutations", "query_parameter_mutations", "response_mutations", "response_trailers_mutations", "request_trailers_mutations")
    REQUEST_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    QUERY_PARAMETER_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TRAILERS_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TRAILERS_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    request_mutations: _containers.RepeatedCompositeFieldContainer[_mutation_rules_pb2.HeaderMutation]
    query_parameter_mutations: _containers.RepeatedCompositeFieldContainer[_base_pb2.KeyValueMutation]
    response_mutations: _containers.RepeatedCompositeFieldContainer[_mutation_rules_pb2.HeaderMutation]
    response_trailers_mutations: _containers.RepeatedCompositeFieldContainer[_mutation_rules_pb2.HeaderMutation]
    request_trailers_mutations: _containers.RepeatedCompositeFieldContainer[_mutation_rules_pb2.HeaderMutation]
    def __init__(self, request_mutations: _Optional[_Iterable[_Union[_mutation_rules_pb2.HeaderMutation, _Mapping]]] = ..., query_parameter_mutations: _Optional[_Iterable[_Union[_base_pb2.KeyValueMutation, _Mapping]]] = ..., response_mutations: _Optional[_Iterable[_Union[_mutation_rules_pb2.HeaderMutation, _Mapping]]] = ..., response_trailers_mutations: _Optional[_Iterable[_Union[_mutation_rules_pb2.HeaderMutation, _Mapping]]] = ..., request_trailers_mutations: _Optional[_Iterable[_Union[_mutation_rules_pb2.HeaderMutation, _Mapping]]] = ...) -> None: ...

class HeaderMutationPerRoute(_message.Message):
    __slots__ = ("mutations",)
    MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    mutations: Mutations
    def __init__(self, mutations: _Optional[_Union[Mutations, _Mapping]] = ...) -> None: ...

class HeaderMutation(_message.Message):
    __slots__ = ("mutations", "most_specific_header_mutations_wins")
    MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    MOST_SPECIFIC_HEADER_MUTATIONS_WINS_FIELD_NUMBER: _ClassVar[int]
    mutations: Mutations
    most_specific_header_mutations_wins: bool
    def __init__(self, mutations: _Optional[_Union[Mutations, _Mapping]] = ..., most_specific_header_mutations_wins: bool = ...) -> None: ...
